import random
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from darknight import logger, xray
from darknight.api.v1.dependencies import authenticate_login
from darknight.db import Session, crud, get_db
from darknight.models.admin import Token
from darknight.models.portal_auth import (
    PortalUser,
    PortalUserResponse,
    RegisterRequest,
    SendCodeRequest,
    hash_password,
)
from darknight.models.proxy import ProxyTypes
from darknight.models.user import UserCreate, UserResponse
from darknight.utils import responses
from darknight.utils.email_sender import send_verification_email
from darknight.utils.jwt import create_user_token

router = APIRouter(tags=["Auth"], responses={401: responses._401})

CODE_EXPIRE_MINUTES = 5
SEND_CODE_COOLDOWN_SECONDS = 60


def _build_default_proxies() -> dict:
    proxies = {}
    for proxy_type in ProxyTypes:
        if xray.config.inbounds_by_protocol.get(proxy_type):
            proxies[proxy_type.value] = {}
    if not proxies:
        raise HTTPException(status_code=503, detail="No proxy protocol is enabled on this server")
    return proxies


def _generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000:06d}"


@router.post("/auth/send-code")
def send_code(
    body: SendCodeRequest,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email = body.email.lower().strip()
    if crud.get_user_by_email(db, email):
        logger.info(f'send-code rejected: email already registered ({email})')
        raise HTTPException(status_code=409, detail="Email is already registered")

    latest = crud.get_latest_verification_code(db, email)
    if latest and (datetime.utcnow() - latest.created_at).total_seconds() < SEND_CODE_COOLDOWN_SECONDS:
        logger.info(f"send-code rejected: cooldown active ({email})")
        raise HTTPException(status_code=429, detail="Please wait before requesting another code")

    from darknight.services.mail import mail

    try:
        mail.ensure_can_send("verification_code", "noreply")
    except (KeyError, FileNotFoundError) as exc:
        logger.error(f"email not configured for verification: {exc}")
        raise HTTPException(status_code=503, detail="Email service is not configured") from exc

    code = _generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES)
    crud.save_email_verification_code(db, email, code, expires_at)
    outbox_id = send_verification_email(
        email, code, expire_minutes=CODE_EXPIRE_MINUTES, background_tasks=bg
    )
    logger.info(f"send-code queued: to={email} outbox_id={outbox_id}")
    return {"detail": "Verification code sent"}


@router.post("/auth/register", response_model=Token, responses={400: responses._400, 409: responses._409})
def register(body: RegisterRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    if crud.get_user_by_email(db, email):
        raise HTTPException(status_code=409, detail="Email is already registered")

    record = crud.get_latest_verification_code(db, email)
    if not record or record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification code expired")
    if record.code != body.code.strip():
        raise HTTPException(status_code=400, detail="Invalid verification code")

    username = email
    if len(username) > 32:
        username = email.split("@")[0][:32]

    proxies = _build_default_proxies()
    new_user = UserCreate(
        username=username,
        status="active",
        proxies=proxies,
        inbounds={},
    )

    for proxy_type in new_user.proxies:
        if not xray.config.inbounds_by_protocol.get(proxy_type):
            raise HTTPException(
                status_code=400,
                detail=f"Protocol {proxy_type} is disabled on your server",
            )

    try:
        dbuser = crud.create_user(
            db,
            new_user,
            email=email,
            hashed_password=hash_password(body.password),
            email_verified_at=datetime.utcnow(),
        )
    except IntegrityError:
        db.rollback()
        suffix = random.randint(100, 999)
        alt_username = f"{username[:28]}_{suffix}"
        new_user.username = alt_username
        try:
            dbuser = crud.create_user(
                db,
                new_user,
                email=email,
                hashed_password=hash_password(body.password),
                email_verified_at=datetime.utcnow(),
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Registration failed, please try again")

    crud.delete_verification_codes(db, email)
    bg.add_task(xray.operations.add_user, dbuser=dbuser)
    logger.info(f'Portal user registered: "{dbuser.username}" ({email})')
    return Token(access_token=create_user_token(dbuser.username), access="user")


@router.post("/auth/token", response_model=Token)
def user_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    token = authenticate_login(db, form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.get("/auth/me", response_model=PortalUserResponse)
def auth_me(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")
    user = UserResponse.model_validate(dbuser)
    return PortalUserResponse(
        username=user.username,
        email=portal_user.email,
        status=user.status.value,
        used_traffic=user.used_traffic,
        data_limit=user.data_limit,
        expire=user.expire,
        subscription_url=user.subscription_url,
        links=user.links,
        created_at=user.created_at,
    )
