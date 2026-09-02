from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    email: str
    notify_expire_email: bool = True
    notify_traffic_email: bool = True


class ProfileUpdateRequest(BaseModel):
    notify_expire_email: bool | None = None
    notify_traffic_email: bool | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)
