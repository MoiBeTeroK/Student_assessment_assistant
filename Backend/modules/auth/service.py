import os

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

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

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    if response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись деактивирована",
        )
    if not response.is_success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка сервиса авторизации",
        )

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


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен или истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )
