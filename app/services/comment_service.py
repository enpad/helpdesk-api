"""Reglas de negocio de comentarios."""

from app.errors import ConflictError
from app.models.comment import Comment, CommentCreate
from app.models.enums import TicketStatus
from app.services.ticket_service import _require
from app.storage.memory import comments


def add(ticket_id: str, data: CommentCreate) -> Comment:
    ticket = _require(ticket_id)
    if ticket.status == TicketStatus.CLOSED:
        raise ConflictError(f"El ticket '{ticket_id}' está cerrado y no admite comentarios")
    return comments.create(ticket_id, data)


def list_for_ticket(ticket_id: str) -> list[Comment]:
    _require(ticket_id)
    return comments.list_for_ticket(ticket_id)
