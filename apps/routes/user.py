# routers/user.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated, List
from database import get_session
from apps.models.models import User
from schema.user import UserCreate, UserReadSimple, UserUpdate
from services.auth_service.auth import get_password_hash
from fastapi import Security
from crud.auth import get_current_user  
from crud.user import get_user_by_id
from services.auth_service.auth import get_password_hash
from fastapi import Security
from schema.voucher import VoucherReadSimple
from schema.transaction import TransactionReadSimple
from schema.package import PackageReadSimple    

router = APIRouter(prefix="/users", tags=["Users"],)

# -------------------------------
# CREATE
# -------------------------------
@router.post("/add_user/", response_model=UserReadSimple,)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        hashed_password=hashed_password,  # à remplacer par un hash réel
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
@router.get("/get_users/", response_model=List[User])
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
    if not user or user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------------
# UPDATE
# -------------------------------
@router.patch("/user/{user_id}", response_model=UserReadSimple)
def update_user(user_id: UUID, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user or db_user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
            setattr(db_user, key, value )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# -------------------------------
# DELETE
# -------------------------------
@router.delete("/user/{user_id}")
async def delete_user(user_id: UUID, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user or db_user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    db_user.statut = "delete"
    session.add(db_user)
    session.commit()
    return {"ok": True}
 
# ------------------------
# Get all vouchers of a user
# ------------------------
@router.get("/{user_id}/vouchers", response_model=List[VoucherReadSimple])
def get_user_vouchers(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user or user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    return user.vouchers

# ------------------------
# Get all transactions of a user
# ------------------------
@router.get("/{user_id}/transactions", response_model=List[TransactionReadSimple])
def get_user_transactions(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user or user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    return user.transactions

# ------------------------
# Get all packages of a user (via transactions)
# ------------------------
@router.get("/{user_id}/packages", response_model=List[PackageReadSimple])
def get_user_packages(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user or user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")

    # Récupère les packages achetés via les transactions
    packages = [transaction.package for transaction in user.transactions if transaction.package]
    return packages
