from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    team: str = Field(default="general")


class Agent(BaseModel):
    id: str
    name: str
    email: str
    team: str
    active: bool = True
