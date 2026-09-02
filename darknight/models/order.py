import secrets
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from darknight.models.product import coerce_feature_list


class PortalOrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    closed = "closed"
    failed = "failed"


class CreateOrderRequest(BaseModel):
    plan_id: str = Field(min_length=1, max_length=32)
    coupon: Optional[str] = Field(default=None, max_length=64)


class OrderResponse(BaseModel):
    id: str
    plan_id: str
    amount: float
    currency: str
    status: PortalOrderStatus
    payment_provider: str
    paypal_order_id: Optional[str] = None
    coupon: Optional[str] = None
    discount: float = 0.0
    wallet_credit: float = 0.0
    created_at: datetime
    paid_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CouponPreviewRequest(BaseModel):
    plan_id: str = Field(min_length=1, max_length=32)
    coupon: str = Field(min_length=1, max_length=64)


class CouponPreviewResponse(BaseModel):
    coupon: str
    currency: str
    original_amount: float
    discount: float
    amount: float


class PayPalConfigResponse(BaseModel):
    client_id: str
    currency: str
    enabled: bool


class PlanResponse(BaseModel):
    plan_id: str
    name_zh: str = ""
    name_en: str = ""
    features_zh: list[str] = Field(default_factory=list)
    features_en: list[str] = Field(default_factory=list)
    price: float
    duration_days: int
    sort_order: int = 0

    @field_validator("features_zh", "features_en", mode="before")
    @classmethod
    def parse_features(cls, value) -> list[str]:
        return coerce_feature_list(value)


class PlanCatalogResponse(BaseModel):
    currency: str
    plans: list[PlanResponse]


class CaptureOrderResponse(BaseModel):
    order: OrderResponse
    detail: str = "Payment captured"


def generate_order_id() -> str:
    now = datetime.utcnow()
    return (
        f"{now:%Y%m%d%H%M%S}"
        f"{secrets.randbelow(1_000_000_000_000):012d}"
    )


__all__ = [
    "CaptureOrderResponse",
    "CouponPreviewRequest",
    "CouponPreviewResponse",
    "CreateOrderRequest",
    "OrderResponse",
    "PayPalConfigResponse",
    "PlanCatalogResponse",
    "PlanResponse",
    "PortalOrderStatus",
    "generate_order_id",
]
