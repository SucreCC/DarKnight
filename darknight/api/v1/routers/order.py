import json
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from darknight import logger, xray
from darknight.db.models import PortalOrder, PortalOrderStatus, User
from darknight.db import Session, crud, get_db
from darknight.models.order import (
    CaptureOrderResponse,
    CouponPreviewRequest,
    CouponPreviewResponse,
    CreateOrderRequest,
    OrderResponse,
    PayPalConfigResponse,
    PlanCatalogResponse,
    PlanResponse,
    generate_order_id,
)
from darknight.models.portal_auth import PortalUser
from darknight.models.product import coerce_feature_list
from darknight.services.config.settings import get_app_config
from darknight.services.payment.coupons import CouponError, resolve_discount
from darknight.services.payment.fulfillment import fulfill_portal_order, try_mark_order_paid
from darknight.services.payment.paypal import (
    PayPalDeclined,
    PayPalError,
    capture_order,
    create_order,
    verify_webhook,
)
from darknight.utils import responses

router = APIRouter(tags=["Orders"], responses={401: responses._401})


def _paypal_config_response() -> PayPalConfigResponse:
    cfg = get_app_config().paypal
    return PayPalConfigResponse(
        client_id=cfg.client_id,
        currency=cfg.currency,
        enabled=cfg.is_configured,
    )


def _ensure_paypal_configured() -> None:
    if not get_app_config().paypal.is_configured:
        raise HTTPException(status_code=503, detail="PayPal payment is not configured")


def _get_user_order(
    order_id: str,
    portal_user: PortalUser,
    db: Session,
):
    order = crud.get_portal_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser or order.user_id != dbuser.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order, dbuser


def _order_response(order: PortalOrder) -> OrderResponse:
    response = OrderResponse.model_validate(order)
    if order.status != PortalOrderStatus.pending:
        return response

    timeout_minutes = get_app_config().paypal.order_timeout_minutes
    if timeout_minutes <= 0:
        return response

    return response.model_copy(
        update={"expires_at": order.created_at + timedelta(minutes=timeout_minutes)}
    )


@router.get("/payments/paypal/config", response_model=PayPalConfigResponse)
def paypal_config():
    return _paypal_config_response()


@router.get("/plans", response_model=PlanCatalogResponse)
def list_plans(db: Session = Depends(get_db)):
    """Authoritative price list. The dashboard renders copy but never prices."""
    products = crud.list_listed_products(db)
    return PlanCatalogResponse(
        currency=get_app_config().paypal.currency,
        plans=[
            PlanResponse(
                plan_id=p.slug,
                name_zh=p.name_zh,
                name_en=p.name_en,
                features_zh=coerce_feature_list(p.features_zh),
                features_en=coerce_feature_list(p.features_en),
                price=p.price,
                duration_days=p.duration_days,
                sort_order=p.sort_order,
            )
            for p in products
        ],
    )


@router.post("/coupons/preview", response_model=CouponPreviewResponse)
def preview_coupon(
    body: CouponPreviewRequest,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    product = crud.get_listed_product(db, body.plan_id)
    if not product:
        raise HTTPException(status_code=400, detail="Invalid plan")

    try:
        code, discount = resolve_discount(body.coupon, product.price)
    except CouponError as exc:
        raise HTTPException(status_code=400, detail="Coupon is invalid or expired") from exc

    return CouponPreviewResponse(
        coupon=code or "",
        currency=get_app_config().paypal.currency,
        original_amount=product.price,
        discount=discount,
        amount=round(product.price - discount, 2),
    )


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_portal_order(
    body: CreateOrderRequest,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    product = crud.get_listed_product(db, body.plan_id)
    if not product:
        raise HTTPException(status_code=400, detail="Invalid plan")

    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        coupon_code, discount = resolve_discount(body.coupon, product.price)
    except CouponError as exc:
        raise HTTPException(status_code=400, detail="Coupon is invalid or expired") from exc

    cfg = get_app_config().paypal
    order = crud.create_portal_order(
        db,
        order_id=generate_order_id(),
        user_id=dbuser.id,
        plan_id=product.slug,
        amount=round(product.price - discount, 2),
        currency=cfg.currency,
        paypal_order_id=None,
        coupon=coupon_code,
        discount=discount,
        snapshot_data_limit_gb=0,
        snapshot_duration_days=product.duration_days,
        snapshot_product_name=product.name_zh,
    )
    return _order_response(order)


@router.post("/orders/{order_id}/prepare-payment", response_model=OrderResponse)
def prepare_order_payment(
    order_id: str,
    refresh: bool = False,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    _ensure_paypal_configured()
    order, _ = _get_user_order(order_id, portal_user, db)

    if order.status != PortalOrderStatus.pending:
        raise HTTPException(status_code=400, detail="Order is not payable")

    # 一张卡提交过之后 PayPal 订单就不可再用，重试必须换一个新的，
    # 否则前端会反复对着已作废的订单提交。
    if order.paypal_order_id and not refresh:
        return _order_response(order)

    cfg = get_app_config().paypal
    try:
        paypal_order_id = create_order(
            amount=order.amount,
            currency=order.currency,
            reference_id=order.id,
        )
    except PayPalError as exc:
        logger.error(f"PayPal create order failed: {exc}")
        raise HTTPException(status_code=502, detail="Failed to create PayPal order") from exc

    order = crud.update_portal_order(db, order, paypal_order_id=paypal_order_id)
    return _order_response(order)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")
    orders = crud.list_portal_orders_for_user(db, dbuser.id)
    return [_order_response(order) for order in orders]


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    order, _ = _get_user_order(order_id, portal_user, db)
    return _order_response(order)


@router.post("/orders/{order_id}/close", response_model=OrderResponse)
def close_order(
    order_id: str,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    order, _ = _get_user_order(order_id, portal_user, db)
    if order.status != PortalOrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be closed")
    order = crud.update_portal_order(db, order, status=PortalOrderStatus.closed)
    return _order_response(order)


@router.post("/orders/{order_id}/capture", response_model=CaptureOrderResponse)
def capture_portal_order(
    order_id: str,
    bg: BackgroundTasks,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    _ensure_paypal_configured()
    order, dbuser = _get_user_order(order_id, portal_user, db)

    if order.status == PortalOrderStatus.paid:
        return CaptureOrderResponse(order=_order_response(order))

    if order.status != PortalOrderStatus.pending:
        raise HTTPException(status_code=400, detail="Order is not payable")

    if not order.paypal_order_id:
        raise HTTPException(status_code=400, detail="PayPal order ID missing")

    try:
        capture_order(order.paypal_order_id)
    except PayPalDeclined as exc:
        # A refused card is recoverable: keep the order payable and drop the spent
        # PayPal order so the next page load prepares a fresh one for another card.
        logger.warning(f"PayPal declined order {order_id}: {exc.code}")
        crud.update_portal_order(db, order, paypal_order_id=None)
        raise HTTPException(status_code=402, detail=f"PAYPAL_DECLINED:{exc.code}") from exc
    except PayPalError as exc:
        logger.error(f"PayPal capture failed for {order_id}: {exc}")
        crud.update_portal_order(db, order, status=PortalOrderStatus.failed)
        raise HTTPException(status_code=502, detail="Payment capture failed") from exc

    if try_mark_order_paid(db, order):
        fulfill_portal_order(db, dbuser, order)
        bg.add_task(xray.operations.update_user, dbuser=dbuser)
        logger.info(f"Order paid: {order.id} user={dbuser.username}")

    return CaptureOrderResponse(order=_order_response(order))


def _extract_paypal_order_id(resource: dict) -> str | None:
    related = resource.get("supplementary_data", {}).get("related_ids", {})
    if related.get("order_id"):
        return related["order_id"]

    for link in resource.get("links", []):
        href = link.get("href", "")
        if link.get("rel") == "up" and "/v2/checkout/orders/" in href:
            return href.rstrip("/").split("/")[-1]
    return None


@router.post("/payments/paypal/webhook")
async def paypal_webhook(
    request: Request,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    cfg = get_app_config().paypal
    if not cfg.webhook_id:
        logger.error("Rejecting PayPal webhook: paypal.webhook_id is not configured")
        raise HTTPException(status_code=503, detail="PayPal webhook is not configured")

    body = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}

    if not verify_webhook(headers, body):
        logger.warning("Rejecting PayPal webhook: signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        event = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Malformed webhook payload")

    if event.get("event_type") != "PAYMENT.CAPTURE.COMPLETED":
        return {"detail": "Ignored"}

    paypal_order_id = _extract_paypal_order_id(event.get("resource", {}))
    if not paypal_order_id:
        return {"detail": "No order id"}

    order = crud.get_portal_order_by_paypal_id(db, paypal_order_id)
    if not order or order.status != PortalOrderStatus.pending:
        return {"detail": "No action needed"}

    dbuser = db.query(User).filter(User.id == order.user_id).first()
    if not dbuser:
        logger.error(f"Webhook order {order.id} references missing user {order.user_id}")
        return {"detail": "User not found"}

    if not try_mark_order_paid(db, order):
        return {"detail": "Already fulfilled"}

    fulfill_portal_order(db, dbuser, order)
    bg.add_task(xray.operations.update_user, dbuser=dbuser)
    logger.info(f"Webhook fulfilled order: {order.id} user={dbuser.username}")
    return {"detail": "Order fulfilled"}
