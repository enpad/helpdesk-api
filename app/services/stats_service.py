"""Agregados de solo lectura sobre los tickets."""

from app.models.enums import TicketPriority, TicketStatus
from app.storage.memory import tickets


def summary() -> dict:
    items = tickets.list_all()
    by_status = {status.value: 0 for status in TicketStatus}
    by_priority = {priority.value: 0 for priority in TicketPriority}

    for ticket in items:
        by_status[ticket.status.value] += 1
        by_priority[ticket.priority.value] += 1

    return {
        "total": len(items),
        "by_status": by_status,
        "by_priority": by_priority,
        "unassigned": len([t for t in items if t.assigned_to is None]),
    }


def workload() -> dict:
    items = tickets.list_all()
    result: dict[str, int] = {}
    for ticket in items:
        if ticket.assigned_to is None:
            continue
        result[ticket.assigned_to] = result.get(ticket.assigned_to, 0) + 1
    return result
