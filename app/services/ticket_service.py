"""Reglas de negocio de tickets que dependen del estado del recurso."""

from app.errors import ConflictError, NotFoundError
from app.models.enums import TicketStatus
from app.models.ticket import Ticket, TicketCreate
from app.storage.memory import tickets

ALLOWED_TRANSITIONS = {
    TicketStatus.OPEN: {TicketStatus.IN_PROGRESS, TicketStatus.PENDING, TicketStatus.CLOSED},
    TicketStatus.IN_PROGRESS: {TicketStatus.OPEN, TicketStatus.PENDING, TicketStatus.CLOSED},
    TicketStatus.PENDING: {TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.CLOSED: {TicketStatus.OPEN},
}


def _require(ticket_id: str) -> Ticket:
    ticket = tickets.get(ticket_id)
    if ticket is None:
        raise NotFoundError(f"El ticket '{ticket_id}' no existe")
    return ticket


def _is_reopen(ticket: Ticket, changes: dict) -> bool:
    """Una reapertura es un cambio que solo mueve el status fuera de 'closed'."""
    requested = changes.get("status")
    if requested is None:
        return False
    if requested == TicketStatus.CLOSED:
        return False
    return len(changes) == 1


def create(data: TicketCreate) -> Ticket:
    return tickets.create(data)


def get(ticket_id: str) -> Ticket:
    return _require(ticket_id)


def update(ticket_id: str, changes: dict) -> Ticket:
    ticket = _require(ticket_id)

    if ticket.status == TicketStatus.CLOSED and not _is_reopen(ticket, changes):
        raise ConflictError(f"El ticket '{ticket_id}' está cerrado y no puede modificarse")

    requested = changes.get("status")
    if requested is not None and requested != ticket.status:
        if requested not in ALLOWED_TRANSITIONS[ticket.status]:
            raise ConflictError(f"No se permite pasar de '{ticket.status.value}' a '{requested}'")

    return tickets.apply_changes(ticket_id, changes)


def delete(ticket_id: str) -> None:
    ticket = _require(ticket_id)
    if ticket.status == TicketStatus.CLOSED:
        raise ConflictError(f"El ticket '{ticket_id}' está cerrado y no puede eliminarse")
    tickets.delete(ticket_id)
