from datetime import datetime

from pydantic import BaseModel


class InviteSummaryResponse(BaseModel):
    balance: float = 0
    currency: str = "USD"
    registered_count: int = 0
    commission_rate: float = 0.10
    pending_commission: float = 0
    total_commission: float = 0


class InviteCodeResponse(BaseModel):
    code: str
    created_at: datetime
    invite_url: str


class InvitePayoutResponse(BaseModel):
    paid_at: datetime
    amount: float
    currency: str = "USD"
