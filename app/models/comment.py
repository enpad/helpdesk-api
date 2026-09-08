from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    author: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class Comment(BaseModel):
    id: str
    ticket_id: str
    author: str
    body: str
    created_at: datetime
