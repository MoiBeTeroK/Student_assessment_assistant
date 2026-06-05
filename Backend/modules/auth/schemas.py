from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh: str


class UserInfo(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    is_active: bool
    date_joined: str
    role: str | None
    passphrase: str | None


class TokenResponse(BaseModel):
    access: str
    refresh: str
    user: UserInfo


class AccessTokenResponse(BaseModel):
    access: str
