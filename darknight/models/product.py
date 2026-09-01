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


class ProductCycleCreate(BaseModel):
    cycle_key: str = Field(min_length=1, max_length=32)
    label_zh: str = Field(min_length=1, max_length=64)
    label_en: str = Field(min_length=1, max_length=64)
    price: float
    data_limit_gb: int
    duration_days: int
    is_listed: bool = False
    sort_order: int = 0

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be > 0")
        return v

    @field_validator("data_limit_gb")
    @classmethod
    def data_limit_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("data_limit_gb must be >= 0")
        return v

    @field_validator("duration_days")
    @classmethod
    def duration_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("duration_days must be > 0")
        return v


class ProductCycleModify(BaseModel):
    cycle_key: Optional[str] = Field(default=None, min_length=1, max_length=32)
    label_zh: Optional[str] = Field(default=None, min_length=1, max_length=64)
    label_en: Optional[str] = Field(default=None, min_length=1, max_length=64)
    price: Optional[float] = None
    data_limit_gb: Optional[int] = None
    duration_days: Optional[int] = None
    is_listed: Optional[bool] = None
    sort_order: Optional[int] = None

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("price must be > 0")
        return v

    @field_validator("data_limit_gb")
    @classmethod
    def data_limit_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("data_limit_gb must be >= 0")
        return v

    @field_validator("duration_days")
    @classmethod
    def duration_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("duration_days must be > 0")
        return v


class ProductCycleResponse(BaseModel):
    id: int
    cycle_key: str
    label_zh: str
    label_en: str
    price: float
    data_limit_gb: int
    duration_days: int
    is_listed: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=32)
    name_zh: str = Field(min_length=1, max_length=128)
    name_en: str = Field(min_length=1, max_length=128)
    category: ProductCategory = "period"
    features_zh: list[str] = Field(default_factory=list)
    features_en: list[str] = Field(default_factory=list)
    display_cycle_key: Optional[str] = Field(default=None, min_length=1, max_length=32)
    sort_order: Optional[int] = None
    is_listed: bool = False
    cycles: list[ProductCycleCreate] = Field(default_factory=list)


class ProductModify(BaseModel):
    slug: Optional[str] = Field(default=None, min_length=1, max_length=32)
    name_zh: Optional[str] = Field(default=None, min_length=1, max_length=128)
    name_en: Optional[str] = Field(default=None, min_length=1, max_length=128)
    category: Optional[ProductCategory] = None
    features_zh: Optional[list[str]] = None
    features_en: Optional[list[str]] = None
    display_cycle_key: Optional[str] = Field(default=None, min_length=1, max_length=32)
    sort_order: Optional[int] = None
    is_listed: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    slug: str
    name_zh: str
    name_en: str
    category: str
    features_zh: list[str]
    features_en: list[str]
    display_cycle_key: str
    sort_order: int
    is_listed: bool
    created_at: datetime
    updated_at: datetime
    cycles: list[ProductCycleResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @field_validator("features_zh", "features_en", mode="before")
    @classmethod
    def parse_features(cls, value: Any) -> list[str]:
        return coerce_feature_list(value)
