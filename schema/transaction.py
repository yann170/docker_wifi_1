from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime,timezone
from uuid import UUID, uuid4



class TransactionReadSimple(SQLModel):
    amount_paid: float
    payment_method: str 
    payment_status: str 
    payment_gateway_ref: Optional[str] = None
    user_id: Optional[int] = None
    package_id: Optional[int] = None


class TransactionCreate(TransactionReadSimple):
    pass


class TransactionUpdate(SQLModel):
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    payment_gateway_ref: Optional[str] = None
    user_id: Optional[int] = None
    package_id: Optional[int] = None


class TransactionReadDetail(SQLModel):
    id: UUID
    amount_paid: float
    payment_method: str 
    payment_status: str 
    payment_gateway_ref: Optional[str] = None
    user_id: Optional[UUID] = None
    package_id: Optional[UUID] = None
    create_at : datetime
