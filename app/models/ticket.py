from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    priority: TicketPriority = TicketPriority.MEDIUM
    requester_email: str = Field(..., min_length=3)


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=200)
    description: str | None = Field(None, min_length=10)
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    assigned_to: str | None = None


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    requester_email: str
    assigned_to: str | None = None
    created_at: datetime
    updated_at: datetime
