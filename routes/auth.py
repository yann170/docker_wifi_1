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
from crud.user import get_user_by_id
from uuid import UUID
from sqlmodel import Session
from typing import List 

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


# @router.get("/users/me/forfaits/")
# async def read_own_forfaits(
#     current_user: Annotated[User, Security(get_current_active_user, scopes=["admin"])],
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]


@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}


router = APIRouter()

@router.put("/users/{user_id}/roles")
async def update_user_roles(
    user_id: UUID,
    new_roles: str, # Par exemple, "admin" ou "user"
    db: Session = Depends(get_session),
    current_user: User = Depends(Security(get_current_user, scopes=["admin"]))
):
    # Vérifier si l'utilisateur à modifier existe
    user = get_user_by_id(db, user_id )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mise à jour des rôles (tu peux stocker ça en JSON, array ou table liée)
    user.role = new_roles
    db.commit()
    db.refresh(user)

    return {"msg": "User roles updated successfully", "user": user.username, "roles": user.role}
