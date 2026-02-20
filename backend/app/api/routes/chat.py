from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import LLMService
from app.services.memory import ConversationMemoryService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ChatResponse:
    memory = ConversationMemoryService(db)
    llm = LLMService()

    conversation_id = memory.upsert_conversation(payload.employee_id, payload.session_id)
    history = memory.fetch_context(
        employee_id=payload.employee_id,
        session_id=payload.session_id,
        window=payload.context_window,
    )
    prompt = memory.build_prompt(history, payload.message)

    ai_response = llm.generate(prompt)

    memory.persist_message(conversation_id, "user", payload.message)
    memory.persist_message(conversation_id, "assistant", ai_response)
    db.commit()

    return ChatResponse(
        session_id=payload.session_id,
        disclaimer=settings.medical_disclaimer,
        response=ai_response,
        used_context_messages=len(history),
    )
