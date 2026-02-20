from collections import deque
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class ConversationMemoryService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_context(self, employee_id: str, session_id: str, window: int) -> list[dict[str, Any]]:
        query = text(
            """
            SELECT m.role, m.content, m.created_at
            FROM messages m
            JOIN conversations c ON c.id = m.conversation_id
            WHERE c.employee_id = :employee_id
              AND c.session_id = :session_id
              AND c.deleted_at IS NULL
            ORDER BY m.created_at DESC
            LIMIT :window
            """
        )
        rows = self.db.execute(
            query, {"employee_id": employee_id, "session_id": session_id, "window": window}
        ).mappings().all()
        return list(reversed(rows))

    def persist_message(self, conversation_id: int, role: str, content: str) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (:conversation_id, :role, :content)
                """
            ),
            {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            },
        )

    def upsert_conversation(self, employee_id: str, session_id: str) -> int:
        row = self.db.execute(
            text(
                """
                INSERT INTO conversations (employee_id, session_id, title)
                VALUES (:employee_id, :session_id, 'Healthcare AI Chat')
                ON CONFLICT (employee_id, session_id)
                DO UPDATE SET updated_at = now()
                RETURNING id
                """
            ),
            {"employee_id": employee_id, "session_id": session_id},
        ).first()
        return row[0]

    @staticmethod
    def build_prompt(history: list[dict[str, Any]], user_message: str) -> str:
        blocks = deque(["System: You are Ali Doctor, a safe healthcare assistant."])
        for item in history:
            blocks.append(f"{item['role'].capitalize()}: {item['content']}")
        blocks.append(f"User: {user_message}")
        blocks.append("Assistant:")
        return "\n".join(blocks)
