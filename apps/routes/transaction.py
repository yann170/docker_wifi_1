from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import select
from typing import List, Optional
from uuid import UUID
from database import get_session
from schema.transaction import  TransactionCreate, TransactionReadSimple, TransactionReadDetail, TransactionUpdate
from apps.models.models import Transaction
from fastapi import APIRouter
from crud.user import get_user_by_id
from crud.package import get_package_by_id

router = APIRouter(prefix="/transaction", tags=["transaction"],)

# ------------------------
# Create transaction
# ------------------------
@router.post("/transactions/", response_model=TransactionReadDetail)
def create_transaction(transaction: TransactionCreate, session=Depends(get_session)):
    if not transaction.user_id or not get_user_by_id(session, transaction.user_id):
        raise HTTPException(status_code=400, detail="Invalid or missing user_id")

    # Vérifier que package_id existe
    if not transaction.package_id or not get_package_by_id(session, transaction.package_id):
        raise HTTPException(status_code=400, detail="Invalid or missing package_id")
    db_transaction = Transaction.model_validate(transaction)
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
    if not transaction or transaction.statut == "delete":
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction_update.model_dump(exclude_unset=True)
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
    transaction.statut = "deleted"
    session.add(transaction)
    session.commit()
    return {"ok": True}
