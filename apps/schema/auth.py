from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class User(BaseModel):
    username: str
    statut: str
    role: str
    numero_telephone: str | None = None

    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
