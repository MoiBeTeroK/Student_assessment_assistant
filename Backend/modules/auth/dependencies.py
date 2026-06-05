from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import service

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    return service.decode_token(credentials.credentials)
