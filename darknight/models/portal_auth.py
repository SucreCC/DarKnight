import re
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator

from darknight.db import Session, crud, get_db
from darknight.models.admin import Token
from darknight.models.user import UserResponse
from darknight.services.config.settings import get_app_config
from darknight.utils.jwt import get_user_payload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

portal_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_app_config().project.api_version}/auth/token"
)

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class SendCodeRequest(BaseModel):
    email: EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)
    password: str = Field(min_length=6, max_length=128)
    invite_code: Optional[str] = None

    @field_validator("code")
    @classmethod
    def strip_code(cls, value: str) -> str:
        return value.strip()


class PortalUser(BaseModel):
    username: str
    email: str
    model_config = {"from_attributes": True}

    @classmethod
    def get_user(cls, token: str, db: Session) -> Optional["PortalUser"]:
        payload = get_user_payload(token)
        if not payload:
            return None
        dbuser = crud.get_user(db, payload["username"])
        if not dbuser or not dbuser.email or not dbuser.hashed_password:
            return None
        return cls(username=dbuser.username, email=dbuser.email)

    @classmethod
    def get_current(
        cls,
        db: Session = Depends(get_db),
        token: str = Depends(portal_oauth2_scheme),
    ) -> "PortalUser":
        user = cls.get_user(token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


class PortalUserResponse(BaseModel):
    username: str
    email: str
    status: str
    used_traffic: int
    data_limit: Optional[int] = None
    expire: Optional[int] = None
    subscription_url: str = ""
    links: list[str] = []
    created_at: datetime
    plan_id: Optional[str] = None
    plan_name_zh: Optional[str] = None
    plan_name_en: Optional[str] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


__all__ = [
    "EMAIL_PATTERN",
    "PortalUser",
    "PortalUserResponse",
    "RegisterRequest",
    "SendCodeRequest",
    "Token",
    "hash_password",
    "portal_oauth2_scheme",
    "verify_password",
]
