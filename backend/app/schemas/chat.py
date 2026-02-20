from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    employee_id: str
    session_id: str
    message: str
    context_window: int = Field(default=12, ge=1, le=50)


class MessageResponse(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    session_id: str
    disclaimer: str
    response: str
    used_context_messages: int
