from fastapi import APIRouter

from . import service
from .schemas import AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login/", response_model=TokenResponse, summary="Вход в систему")
async def login(data: LoginRequest):
    return await service.login(data.username, data.password)


@router.post(
    "/refresh/",
    response_model=AccessTokenResponse,
    summary="Обновление access-токена",
)
async def refresh(data: RefreshRequest):
    return await service.refresh_token(data.refresh)
