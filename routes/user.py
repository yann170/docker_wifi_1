# routers/user.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated, List
from database import get_session
from models import User
from schema.user import UserCreate, UserReadSimple, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------------
# CREATE
# -------------------------------
@router.post("/add_user/", response_model=UserReadSimple)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(
        username=user.username,
        hashed_password=user.password, 
        email=user.email,
        numero=user.numero
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# -------------------------------
# READ LIST
# -------------------------------
@router.get("/get_users/", response_model=List[UserReadSimple])
def read_users(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

# -------------------------------
# READ SINGLE
# -------------------------------
@router.get("/user/{user_id}", response_model=UserReadSimple)
def read_user(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------------
# UPDATE
# -------------------------------
@router.patch("/user/{user_id}", response_model=UserReadSimple)
def update_user(user_id: UUID, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            setattr(db_user, "hashed_password", value)  # penser à hasher
        else:
            setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# -------------------------------
# DELETE
# -------------------------------
@router.delete("/user/{user_id}")
def delete_user(user_id: UUID, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)
    session.commit()
    return {"ok": True}
