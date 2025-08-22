from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from schema.auth import User, UserInDB,Token,TokenData
from database import get_session
from typing import Annotated
from datetime import timedelta

from config import config   
from crud.auth import oauth2_scheme
from fastapi import APIRouter
from services.auth_service.auth import (
    authenticate_user,
    create_access_token,
)
from crud.auth import get_current_active_user
from crud.auth import get_current_user
from config import config

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["admin"])],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}