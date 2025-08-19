from typing import Optional, Union, Sequence
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone 
from schema.voucher import VoucherReadSimple
from schema.transaction import TransactionReadSimple
from uuid import UUID, uuid4
from typing import List
from pydantic import EmailStr



class UserCreate(SQLModel):
    username: str
    password: str  
    email: Optional[EmailStr] = None
    numero: Optional[str] = None

class UserReadSimple(SQLModel):
    id: UUID  
    username: str
    email: Optional[EmailStr] = None
    created_at: datetime
    numero: Optional[str] = None

class UserReadDetail(UserReadSimple):
    vouchers: List[VoucherReadSimple] = [] 
    transactions: List[TransactionReadSimple] = []

class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    numero: Optional[str] = None
   

class UserDelete(SQLModel):
    id: UUID  
