# crud/user.py
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select
from models import User
from schema.user import UserCreate, UserReadSimple, UserReadDetail, UserUpdate

# -------------------------------
# CREATE
# -------------------------------
def create_user(session: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        hashed_password=user.password,  # à remplacer par un hash réel
        email=user.email,
        numero=user.numero
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# -------------------------------
# READ
# -------------------------------
def get_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return session.exec(stmt).first()

# def list_users(session: Session, offset: int = 0, limit: int = 100) -> List[User]:
#     stmt = select(User).offset(offset).limit(limit)
#     return session.exec(stmt).all()

# -------------------------------
# UPDATE
# -------------------------------
def update_user(session: Session, user_id: UUID, user_update: UserUpdate) -> User|None:
    db_user = get_user_by_id(session, user_id)
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
def delete_user(session: Session, user_id: UUID) -> bool:
    db_user = get_user_by_id(session, user_id)
    session.delete(db_user)
    session.commit()
    return True
