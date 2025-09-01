# crud/user.py
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select
from models import User
from schema.user import UserCreate, UserReadSimple, UserReadDetail, UserUpdate


def get_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
    user = session.get(User, user_id)
    if not user or user.statut == "delete" :
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()
    if not user or user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    print("User found:", user)    
    return user


def get_role_by_username(session: Session, username: str) -> Optional[str]:
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()
    if user and user.statut != "delete":
        return user.role
    return None