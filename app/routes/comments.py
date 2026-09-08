from fastapi import APIRouter

from app.models.comment import Comment, CommentCreate
from app.services import comment_service

router = APIRouter(prefix="/tickets", tags=["comments"])


@router.post("/{ticket_id}/comments", response_model=Comment, status_code=201)
def add_comment(ticket_id: str, payload: CommentCreate):
    return comment_service.add(ticket_id, payload)


@router.get("/{ticket_id}/comments", response_model=list[Comment])
def list_comments(ticket_id: str):
    return comment_service.list_for_ticket(ticket_id)
