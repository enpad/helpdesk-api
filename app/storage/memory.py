"""Almacenamiento en memoria. CRUD puro: sin reglas de negocio, sin códigos HTTP."""

from datetime import datetime
from uuid import uuid4

from app.models.agent import Agent, AgentCreate
from app.models.comment import Comment, CommentCreate
from app.models.enums import TicketStatus
from app.models.ticket import Ticket, TicketCreate


class TicketStore:
    def __init__(self):
        self._items: dict[str, Ticket] = {}

    def create(self, data: TicketCreate) -> Ticket:
        now = datetime.now()
        ticket = Ticket(
            id=str(uuid4()),
            title=data.title,
            description=data.description,
            priority=data.priority,
            status=TicketStatus.OPEN,
            requester_email=data.requester_email,
            assigned_to=None,
            created_at=now,
            updated_at=now,
        )
        self._items[ticket.id] = ticket
        return ticket

    def get(self, ticket_id: str) -> Ticket | None:
        return self._items.get(ticket_id)

    def list_all(self) -> list[Ticket]:
        return list(self._items.values())

    def apply_changes(self, ticket_id: str, changes: dict) -> Ticket:
        ticket = self._items[ticket_id]
        for field, value in changes.items():
            if value is None:
                continue
            setattr(ticket, field, value)
        ticket.updated_at = datetime.now()
        return ticket

    def delete(self, ticket_id: str) -> None:
        self._items.pop(ticket_id, None)

    def clear(self) -> None:
        self._items.clear()


class CommentStore:
    def __init__(self):
        self._items: dict[str, Comment] = {}

    def create(self, ticket_id: str, data: CommentCreate) -> Comment:
        comment = Comment(
            id=str(uuid4()),
            ticket_id=ticket_id,
            author=data.author,
            body=data.body,
            created_at=datetime.now(),
        )
        self._items[comment.id] = comment
        return comment

    def list_for_ticket(self, ticket_id: str) -> list[Comment]:
        return [c for c in self._items.values() if c.ticket_id == ticket_id]

    def clear(self) -> None:
        self._items.clear()


class AgentStore:
    def __init__(self):
        self._items: dict[str, Agent] = {}

    def create(self, data: AgentCreate) -> Agent:
        agent = Agent(id=str(uuid4()), name=data.name, email=data.email, team=data.team, active=True)
        self._items[agent.id] = agent
        return agent

    def get(self, agent_id: str) -> Agent | None:
        return self._items.get(agent_id)

    def get_by_email(self, email: str) -> Agent | None:
        for agent in self._items.values():
            if agent.email == email:
                return agent
        return None

    def list_all(self) -> list[Agent]:
        return list(self._items.values())

    def clear(self) -> None:
        self._items.clear()


tickets = TicketStore()
comments = CommentStore()
agents = AgentStore()
