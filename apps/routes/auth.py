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
from crud.user import get_role_by_username, get_user_by_username
from services.auth_service.auth import create_refresh_token
from jose import jwt, JWTError 

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/users/me/", response_model=UserReadSimple) 
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.statut != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return {"status": "active", "user": current_user.username}

#-------------------------------
# LOGIN - TOKEN
#-------------------------------
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Access token court
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_scopes = get_role_by_username(session, form_data.username)  # renvoie ["admin"] ou ["user"]
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user_scopes},
        expires_delta=access_token_expires,
    )

    # Refresh token longue durée
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token
    )

#-------------------------------
# REFRESH TOKEN
#-------------------------------

@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
    
        if not username:
            raise HTTPException(status_code=401, detail="Refresh token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token invalide")

    # Vérifier que l'utilisateur existe toujours
    user = get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    # Créer un nouvel access token
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_scopes = get_role_by_username(session, username)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user_scopes},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




# -------------------------------
# UPDATE USER ROLES (ADMIN ONLY)
# -------------------------------
@router.put("/roles")
async def update_user_roles(
    user_id: UUID,
    new_roles: str,
    current_user: Annotated[User, Security(get_current_user, scopes=["admin"])],
    db: Session = Depends(get_session)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    allowed_roles = ["admin", "user"]
    if new_roles not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.role = new_roles
    db.commit()
    db.refresh(user)

    return {"msg": "User roles updated successfully", "user": user.username, "roles": user.role}
