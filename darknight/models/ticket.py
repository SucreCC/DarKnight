from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TicketPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class TicketStatus(str, Enum):
    open = "open"
    pending = "pending"
    resolved = "resolved"
    closed = "closed"


class TicketAuthorType(str, Enum):
    user = "user"
    admin = "admin"


class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=256)
    priority: TicketPriority = TicketPriority.normal
    content: str = Field(min_length=1, max_length=10000)


class TicketReplyCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class TicketUserModify(BaseModel):
    status: Optional[TicketStatus] = None


class TicketAdminModify(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None


class TicketReplyResponse(BaseModel):
    id: int
    author_type: TicketAuthorType
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketListItem(BaseModel):
    id: int
    subject: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    last_reply_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TicketDetail(TicketListItem):
    replies: list[TicketReplyResponse]


class AdminTicketListItem(TicketListItem):
    username: str
