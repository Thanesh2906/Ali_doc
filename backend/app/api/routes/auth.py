from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# Replace with DB-backed users + RBAC in production.
FAKE_USERS = {"admin": {"password": hash_password("admin123"), "role": "admin"}}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = FAKE_USERS.get(payload.username)
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=payload.username,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenResponse(access_token=token)
