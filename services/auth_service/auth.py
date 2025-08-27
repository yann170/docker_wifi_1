import jwt # type: ignore
from fastapi import Depends, FastAPI, HTTPException, Security, status
from schema.auth import User, UserInDB,Token,TokenData
from passlib.context import CryptContext # pyright: ignore[reportMissingModuleSource]
from datetime import datetime, timedelta, timezone
from database import get_session
from sqlmodel import select
from models import User as UserModel
from crud.user import get_user_by_username
from config import config
from typing import Annotated
from sqlmodel import Session
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from crud.user import get_role_by_username

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)



def authenticate_user(username: str, password: str, session: Session = Depends(get_session)):
    user = get_user_by_username(session, username)
    password = get_password_hash(password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    else :
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect password")
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    user_role = get_role_by_username(session, form_data.username)

    if user_role == "admin":
        form_data.scopes.append("admin")
    else:
        form_data.scopes.append("user")   

    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
