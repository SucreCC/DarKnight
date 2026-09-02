from datetime import datetime
import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


ProductCategory = Literal["period", "traffic"]


def coerce_feature_list(value: Any) -> list[str]:
    """SQLite 迁移里若用 json.dumps 写入 JSON 列，读出来可能是 str 而非 list。"""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
        return [text]
    return []


class ProductCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=32)
    name_zh: str = Field(min_length=1, max_length=128)
    name_en: str = Field(min_length=1, max_length=128)
    category: ProductCategory = "period"
    features_zh: list[str] = Field(default_factory=list)
    features_en: list[str] = Field(default_factory=list)
    price: float
    duration_days: int
    sort_order: Optional[int] = None
    is_listed: bool = False

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be > 0")
        return v

    @field_validator("duration_days")
    @classmethod
    def duration_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("duration_days must be > 0")
        return v


class ProductModify(BaseModel):
    slug: Optional[str] = Field(default=None, min_length=1, max_length=32)
    name_zh: Optional[str] = Field(default=None, min_length=1, max_length=128)
    name_en: Optional[str] = Field(default=None, min_length=1, max_length=128)
    category: Optional[ProductCategory] = None
    features_zh: Optional[list[str]] = None
    features_en: Optional[list[str]] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    sort_order: Optional[int] = None
    is_listed: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("price must be > 0")
        return v

    @field_validator("duration_days")
    @classmethod
    def duration_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("duration_days must be > 0")
        return v


class ProductResponse(BaseModel):
    id: int
    slug: str
    name_zh: str
    name_en: str
    category: str
    features_zh: list[str]
    features_en: list[str]
    price: float
    duration_days: int
    sort_order: int
    is_listed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("features_zh", "features_en", mode="before")
    @classmethod
    def parse_features(cls, value: Any) -> list[str]:
        return coerce_feature_list(value)
