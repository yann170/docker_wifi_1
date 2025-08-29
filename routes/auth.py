from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from schema.auth import User,Token
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
from crud.user import get_user_by_id
from uuid import UUID
from sqlmodel import Session
from typing import List 
from schema.user import UserReadSimple
from services.auth_service.auth import authenticate_user, create_access_token
from datetime import timedelta
from schema.auth import Token
from fastapi.security import OAuth2PasswordRequestForm  



router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/users/me/", response_model=UserReadSimple) 
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}


