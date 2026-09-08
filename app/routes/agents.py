from fastapi import APIRouter
from pydantic import BaseModel

from app.models.agent import Agent, AgentCreate
from app.models.ticket import Ticket
from app.services import assignment_service
from app.storage.memory import agents

router = APIRouter(tags=["agents"])


class AssignRequest(BaseModel):
    agent_email: str


@router.get("/agents", response_model=list[Agent])
def list_agents():
    return agents.list_all()


@router.post("/agents", response_model=Agent, status_code=201)
def create_agent(payload: AgentCreate):
    return agents.create(payload)


@router.post("/tickets/{ticket_id}/assign", response_model=Ticket)
def assign_ticket(ticket_id: str, payload: AssignRequest):
    return assignment_service.assign(ticket_id, payload.agent_email)


@router.delete("/tickets/{ticket_id}/assign", response_model=Ticket)
def unassign_ticket(ticket_id: str):
    return assignment_service.unassign(ticket_id)
