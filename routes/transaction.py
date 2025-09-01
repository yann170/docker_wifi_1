from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from database import get_session, create_table_in_db
from schema.transaction import  TransactionCreate, TransactionReadSimple, TransactionReadDetail, TransactionUpdate
from models import Transaction
from sqlmodel import Session
from fastapi import APIRouter

router = APIRouter(prefix="/transaction", tags=["transaction"],)

# ------------------------
# Create transaction
# ------------------------
@router.post("/transactions/", response_model=TransactionReadDetail)
def create_transaction(transaction: TransactionCreate, session=Depends(get_session)):
    db_transaction = Transaction.from_orm(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

# ------------------------
# Read all transactions (simple)
# ------------------------
@router.get("/transactions/", response_model=List[TransactionReadSimple])
def read_transactions(session=Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    return transactions

# ------------------------
# Read transaction by ID (detail)
# ------------------------
@router.get("/transactions/{transaction_id}", response_model=TransactionReadDetail)
def read_transaction(transaction_id: UUID, session=Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# ------------------------
# Update transaction
# ------------------------
@router.patch("/transactions/{transaction_id}", response_model=TransactionReadDetail)
def update_transaction(transaction_id: UUID, transaction_update: TransactionUpdate, session=Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)
    
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

# ------------------------
# Delete transaction
# ------------------------
@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: UUID, session=Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}
