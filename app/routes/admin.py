from fastapi import APIRouter, HTTPException, status

from app.db.mongo import master_db
from app.schemas.auth import AdminLoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(payload: AdminLoginRequest) -> TokenResponse:
    service = AuthService(master_db=master_db())
    token = await service.login(email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)
