import logging

from fastapi import APIRouter, Query

from app import config
from app.models.enums import TicketPriority, TicketStatus
from app.models.ticket import Ticket, TicketCreate, TicketUpdate
from app.services import stats_service, ticket_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=Ticket, status_code=201)
def create_ticket(payload: TicketCreate):
    ticket = ticket_service.create(payload)
    logger.info("Ticket %s creado por %s", ticket.id, payload.requester_email)
    return ticket


@router.get("", response_model=list[Ticket])
def list_tickets(
    status: TicketStatus | None = Query(None),
    priority: TicketPriority | None = Query(None),
    assigned_to: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(config.DEFAULT_PAGE_SIZE, ge=1, le=config.MAX_PAGE_SIZE),
):
    from app.storage.memory import tickets as store

    items = store.list_all()
    if status is not None:
        items = [t for t in items if t.status == status]
    if priority is not None:
        items = [t for t in items if t.priority == priority]
    if assigned_to is not None:
        items = [t for t in items if t.assigned_to == assigned_to]
    return items[skip : skip + limit]


@router.get("/stats/summary")
def ticket_stats():
    return stats_service.summary()


@router.get("/stats/workload")
def ticket_workload():
    return stats_service.workload()


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str):
    return ticket_service.get(ticket_id)


@router.patch("/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: str, payload: TicketUpdate):
    changes = payload.model_dump(exclude_unset=True)
    return ticket_service.update(ticket_id, changes)


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: str):
    ticket_service.delete(ticket_id)
    return None
