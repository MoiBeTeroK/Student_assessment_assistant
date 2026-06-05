import os

from fastapi import APIRouter, HTTPException, Request, Response, status

from . import service
from .schemas import AccessTokenResponse, LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])

REFRESH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 дней — совпадает с Django REFRESH_TOKEN_LIFETIME
SECURE_COOKIE = os.getenv("SECURE_COOKIE", "false").lower() == "true"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/api/auth/refresh/",
    )


@router.post("/login/", response_model=LoginResponse, summary="Вход в систему")
async def login(data: LoginRequest, response: Response):
    result = await service.login(data.username, data.password)
    _set_refresh_cookie(response, result["refresh"])
    return {"access": result["access"], "user": result["user"]}


@router.post(
    "/refresh/",
    response_model=AccessTokenResponse,
    summary="Обновление access-токена",
)
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh-токен отсутствует",
        )
    result = await service.refresh_token(refresh_token)
    # Django с ROTATE_REFRESH_TOKENS=True возвращает новый refresh — обновляем cookie
    if "refresh" in result:
        _set_refresh_cookie(response, result["refresh"])
    return {"access": result["access"]}


@router.post("/logout/", summary="Выход из системы")
async def logout(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await service.logout(refresh_token)
    response.delete_cookie(key="refresh_token", path="/api/auth/refresh/")
    return {"detail": "Выход выполнен"}
