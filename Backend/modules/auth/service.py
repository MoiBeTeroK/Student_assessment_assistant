import os

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import text

ADMIN_PANEL_URL = os.getenv("ADMIN_PANEL_URL", "http://localhost:8001")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"


async def login(username: str, password: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ADMIN_PANEL_URL}/api/auth/login/",
                json={"username": username, "password": password},
                timeout=10.0,
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис авторизации недоступен",
            )

    if not response.is_success:
        detail = response.json().get("detail", "Ошибка авторизации") if response.content else "Ошибка авторизации"
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


async def refresh_token(refresh: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ADMIN_PANEL_URL}/api/auth/refresh/",
                json={"refresh": refresh},
                timeout=10.0,
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис авторизации недоступен",
            )

    if not response.is_success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh-токен недействителен или истёк",
        )

    return response.json()


async def logout(refresh: str) -> None:
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{ADMIN_PANEL_URL}/api/auth/logout/",
                json={"refresh": refresh},
                timeout=10.0,
            )
        except httpx.RequestError:
            pass  # Блэклист best-effort: cookie всё равно очистим


def decode_token(token: str, db: Session | None = None) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен или истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if db is not None:
        user_id = payload.get("user_id")
        if user_id:
            row = db.execute(
                text("SELECT active_jti FROM user_profile WHERE user_id = :uid"),
                {"uid": user_id},
            ).fetchone()
            if row is not None and row[0] == '':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Сессия завершена",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    return payload
