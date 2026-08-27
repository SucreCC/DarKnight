import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from darknight import logger, xray
from darknight.db.models import PortalOrderStatus, User
from darknight.db import Session, crud, get_db
from darknight.models.order import (
    CaptureOrderResponse,
    CouponPreviewRequest,
    CouponPreviewResponse,
    CreateOrderRequest,
    OrderResponse,
    PayPalConfigResponse,
    PlanCatalogResponse,
    PlanCycleResponse,
    PlanResponse,
    generate_order_id,
)
from darknight.models.portal_auth import PortalUser
from darknight.services.config.settings import get_app_config
from darknight.services.payment.coupons import CouponError, resolve_discount
from darknight.services.payment.fulfillment import fulfill_portal_order, try_mark_order_paid
from darknight.services.payment.paypal import PayPalError, capture_order, create_order, verify_webhook
from darknight.services.payment.plans import get_plan_cycle, group_plan_catalog
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


@router.get("/payments/paypal/config", response_model=PayPalConfigResponse)
def paypal_config():
    return _paypal_config_response()


@router.get("/plans", response_model=PlanCatalogResponse)
def list_plans():
    """Authoritative price list. The dashboard renders copy but never prices."""
    return PlanCatalogResponse(
        currency=get_app_config().paypal.currency,
        plans=[
            PlanResponse(
                plan_id=plan_id,
                cycles=[
                    PlanCycleResponse(
                        cycle_id=cycle_id,
                        price=cycle.price,
                        data_limit_gb=cycle.data_limit_gb,
                        duration_days=cycle.duration_days,
                    )
                    for cycle_id, cycle in cycles
                ],
            )
            for plan_id, cycles in group_plan_catalog().items()
        ],
    )


@router.post("/coupons/preview", response_model=CouponPreviewResponse)
def preview_coupon(
    body: CouponPreviewRequest,
    portal_user: PortalUser = Depends(PortalUser.get_current),
):
    plan = get_plan_cycle(body.plan_id, body.cycle_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan or billing cycle")

    try:
        code, discount = resolve_discount(body.coupon, plan.price)
    except CouponError as exc:
        raise HTTPException(status_code=400, detail="Coupon is invalid or expired") from exc

    return CouponPreviewResponse(
        coupon=code or "",
        currency=get_app_config().paypal.currency,
        original_amount=plan.price,
        discount=discount,
        amount=round(plan.price - discount, 2),
    )


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_portal_order(
    body: CreateOrderRequest,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    plan = get_plan_cycle(body.plan_id, body.cycle_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan or billing cycle")

    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        coupon_code, discount = resolve_discount(body.coupon, plan.price)
    except CouponError as exc:
        raise HTTPException(status_code=400, detail="Coupon is invalid or expired") from exc

    cfg = get_app_config().paypal
    order = crud.create_portal_order(
        db,
        order_id=generate_order_id(),
        user_id=dbuser.id,
        plan_id=body.plan_id,
        cycle_id=body.cycle_id,
        amount=round(plan.price - discount, 2),
        currency=cfg.currency,
        paypal_order_id=None,
        coupon=coupon_code,
        discount=discount,
    )
    return OrderResponse.model_validate(order)


@router.post("/orders/{order_id}/prepare-payment", response_model=OrderResponse)
def prepare_order_payment(
    order_id: str,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    _ensure_paypal_configured()
    order, _ = _get_user_order(order_id, portal_user, db)

    if order.status != PortalOrderStatus.pending:
        raise HTTPException(status_code=400, detail="Order is not payable")

    if order.paypal_order_id:
        return OrderResponse.model_validate(order)

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
    return OrderResponse.model_validate(order)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")
    orders = crud.list_portal_orders_for_user(db, dbuser.id)
    return [OrderResponse.model_validate(order) for order in orders]


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    order, _ = _get_user_order(order_id, portal_user, db)
    return OrderResponse.model_validate(order)


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
    return OrderResponse.model_validate(order)


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
        return CaptureOrderResponse(order=OrderResponse.model_validate(order))

    if order.status != PortalOrderStatus.pending:
        raise HTTPException(status_code=400, detail="Order is not payable")

    if not order.paypal_order_id:
        raise HTTPException(status_code=400, detail="PayPal order ID missing")

    try:
        capture_order(order.paypal_order_id)
    except PayPalError as exc:
        logger.error(f"PayPal capture failed for {order_id}: {exc}")
        crud.update_portal_order(db, order, status=PortalOrderStatus.failed)
        raise HTTPException(status_code=502, detail="Payment capture failed") from exc

    if try_mark_order_paid(db, order):
        fulfill_portal_order(db, dbuser, order)
        bg.add_task(xray.operations.update_user, dbuser=dbuser)
        logger.info(f"Order paid: {order.id} user={dbuser.username}")

    return CaptureOrderResponse(order=OrderResponse.model_validate(order))


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
