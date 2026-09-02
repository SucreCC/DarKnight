from fastapi import APIRouter, Depends, HTTPException, Request

from darknight.db import Session, crud, get_db
from darknight.models.invite import InviteCodeResponse, InvitePayoutResponse, InviteSummaryResponse
from darknight.models.portal_auth import PortalUser
from darknight.services.payment.referral import COMMISSION_RATE, _commission_currency
from darknight.utils import responses
from darknight.utils.invite import build_invite_register_url

router = APIRouter(tags=["Invite"], responses={401: responses._401})


def _get_db_user(portal_user: PortalUser, db: Session):
    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")
    return dbuser


def _invite_code_response(request: Request, row) -> InviteCodeResponse:
    return InviteCodeResponse(
        code=row.code,
        created_at=row.created_at,
        invite_url=build_invite_register_url(request, row.code),
    )


@router.get("/invite/summary", response_model=InviteSummaryResponse)
def invite_summary(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    balance, pending, total, currency = crud.get_invite_commission_summary(db, dbuser.id)
    return InviteSummaryResponse(
        balance=balance,
        currency=currency or _commission_currency(),
        registered_count=crud.count_referred_users(db, dbuser.id),
        commission_rate=COMMISSION_RATE,
        pending_commission=pending,
        total_commission=total,
    )


@router.get("/invite/payouts", response_model=list[InvitePayoutResponse])
def list_invite_payouts(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    crud.promote_due_referral_commissions(db, dbuser.id)
    rows = crud.list_commission_payouts(db, dbuser.id)
    return [
        InvitePayoutResponse(
            paid_at=row.created_at,
            amount=row.amount,
            currency=row.currency or _commission_currency(),
        )
        for row in rows
    ]


@router.get("/invite/codes", response_model=list[InviteCodeResponse])
def list_invite_codes(
    request: Request,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    rows = crud.list_invite_codes_for_user(db, dbuser.id)
    return [_invite_code_response(request, row) for row in rows]


@router.post("/invite/codes", response_model=InviteCodeResponse)
def create_invite_code(
    request: Request,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    try:
        row = crud.create_invite_code_for_user(db, dbuser.id)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="Failed to generate invite code") from exc
    return _invite_code_response(request, row)
