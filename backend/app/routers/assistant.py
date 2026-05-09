from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.assistant_service import build_context_json, chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    property_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    context = build_context_json(current_user.id, db, body.property_id)
    reply = chat(body.message, context)
    return ChatResponse(reply=reply)
