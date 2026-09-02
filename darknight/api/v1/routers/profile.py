from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from darknight import logger, xray
from darknight.db import Session, crud, get_db
from darknight.models.portal_auth import PortalUser, hash_password, verify_password
from darknight.models.profile import (
    ChangePasswordRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from darknight.utils import responses

router = APIRouter(tags=["Profile"], responses={401: responses._401})


def _get_db_user(portal_user: PortalUser, db: Session):
    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")
    return dbuser


def _profile_response(dbuser) -> ProfileResponse:
    return ProfileResponse(
        email=dbuser.email or "",
        notify_expire_email=bool(dbuser.notify_expire_email),
        notify_traffic_email=bool(dbuser.notify_traffic_email),
    )


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    return _profile_response(_get_db_user(portal_user, db))


@router.patch("/profile", response_model=ProfileResponse)
def update_profile(
    body: ProfileUpdateRequest,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    updates = body.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(dbuser, key, value)
    db.add(dbuser)
    db.commit()
    db.refresh(dbuser)
    return _profile_response(dbuser)


@router.post("/profile/change-password")
def change_password(
    body: ChangePasswordRequest,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    if not dbuser.hashed_password or not verify_password(body.old_password, dbuser.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    if body.old_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password must differ from old password")

    dbuser.hashed_password = hash_password(body.new_password)
    db.add(dbuser)
    db.commit()
    return {"detail": "Password updated"}


@router.post("/profile/revoke-subscription")
def revoke_subscription(
    bg: BackgroundTasks,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    dbuser = crud.revoke_user_sub(db, dbuser)
    bg.add_task(xray.operations.update_user, dbuser=dbuser)
    logger.info(f'Portal user "{dbuser.username}" revoked subscription')
    return {"detail": "Subscription reset"}
