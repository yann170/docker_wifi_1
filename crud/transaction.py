# crud/transaction.py
from typing import Optional
from sqlmodel import Session, select
from models import Transaction, User
from uuid import UUID
from fastapi import HTTPException

def create_transaction(session: Session, *, transaction_id: str, user_id: UUID,
                       amount: float, package_id: UUID,
                       payment_method: str , status: str = "PENDING") -> Transaction:
    tx = Transaction(
        payment_gateway_ref=transaction_id,
        user_id=user_id,
        amount_paid=amount,
        package_id=package_id,
        payment_method=payment_method,
        payment_status=status,
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx

def get_transaction_by_txid(session: Session, transaction_id: str) -> Optional[Transaction]:
    stmt = select(Transaction).where(Transaction.payment_gateway_ref== transaction_id and Transaction.statut !="delete")
    if not transaction_id or transaction_id.strip() == "" :
        raise HTTPException(status_code=400, detail="Transaction ID is required")
    if not session:
        raise HTTPException(status_code=500, detail="Database session is not available")
    return session.exec(stmt).first()


def update_transaction_status(session: Session, transaction_id: str, new_status: str, method:str | None ) -> Optional[Transaction]:
    tx = get_transaction_by_txid(session, transaction_id)
    if not tx or tx.statut == "delete":
        return None
    tx.payment_status = new_status
    tx.payment_method = method 
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


def get_user_email_by_user_id(session: Session, user_id: UUID) -> Optional[str]:
    stmt = select(User).where(User.id == user_id and User.statut !="delete" )
    user_email= session.exec(stmt).first()
    if user_email:
        return user_email.email
    return None
    
def get_email_by_transaction_id(session: Session, transaction_id: str) -> Optional[str]:
    tx = get_transaction_by_txid(session, transaction_id)
    if not tx or tx.statut == "delete":
        return None
    user_email = get_user_email_by_user_id(session, tx.user_id)
    return user_email