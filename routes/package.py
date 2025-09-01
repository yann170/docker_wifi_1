from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated, List
from uuid import UUID
from database import get_session
from models import Transaction
from schema.transaction import TransactionCreate, TransactionReadSimple, TransactionReadDetail, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# ------------------------
# Create transaction
# ------------------------
@router.post("/add/", response_model=TransactionReadDetail)
async def create_transaction(transaction: TransactionCreate, session: Session = Depends(get_session)):
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

# ------------------------
# Read all transactions (simple)
# ------------------------
@router.get("/get_all/", response_model=List[TransactionReadSimple])
async def read_transactions(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    transactions = session.exec(select(Transaction).offset(offset).limit(limit)).all()
    return transactions

# ------------------------
# Read transaction by ID (detail)
# ------------------------
@router.get("/get/{transaction_id}", response_model=TransactionReadDetail)
def read_transaction(transaction_id: UUID, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# ------------------------
# Update transaction
# ------------------------
@router.patch("/update/{transaction_id}", response_model=TransactionReadDetail)
def update_transaction(transaction_id: UUID, transaction_update: TransactionUpdate, session: Session = Depends(get_session)):
    transaction_db = session.get(Transaction, transaction_id)
    if not transaction_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction_update.model_dump(exclude_unset=True) if hasattr(transaction_update, "model_dump") else transaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction_db, key, value)
    
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)
    return transaction_db

# ------------------------
# Delete transaction
# ------------------------
@router.delete("/delete/{transaction_id}")
def delete_transaction(transaction_id: UUID, session: Session = Depends(get_session)):
    transaction_db = session.get(Transaction, transaction_id)
    if not transaction_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction_db)
    session.commit()
    return {"ok": True}
