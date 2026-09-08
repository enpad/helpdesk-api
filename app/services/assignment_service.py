"""Reglas de negocio de asignación de tickets a agentes."""

from app.errors import ConflictError, NotFoundError
from app.models.enums import TicketStatus
from app.models.ticket import Ticket
from app.services.ticket_service import _require
from app.storage.memory import agents, tickets


def assign(ticket_id: str, agent_email: str) -> Ticket:
    ticket = _require(ticket_id)

    agent = agents.get_by_email(agent_email)
    if agent is None:
        raise NotFoundError(f"No existe un agente con el correo '{agent_email}'")
    if not agent.active:
        raise ConflictError(f"El agente '{agent_email}' está inactivo")
    if ticket.status == TicketStatus.CLOSED:
        raise ConflictError(f"El ticket '{ticket_id}' está cerrado y no puede reasignarse")

    return tickets.apply_changes(ticket_id, {"assigned_to": agent_email})


def unassign(ticket_id: str) -> Ticket:
    ticket = _require(ticket_id)
    if ticket.assigned_to is None:
        raise ConflictError(f"El ticket '{ticket_id}' no está asignado")
    ticket.assigned_to = None
    return ticket
