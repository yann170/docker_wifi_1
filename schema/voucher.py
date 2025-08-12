from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4


class VoucherReadSimple(SQLModel):
    id: UUID
    username_voucher: str
    password_voucher: str
    created_at: datetime
    package_id: Optional[int]
    gernerated_at: datetime
    user_id: Optional[int]
        


class VoucherCreate(SQLModel):
    user_id: Optional[int] 
    package_id: Optional[int] 
    username_voucher: str
    password_voucher: str


class VoucherReadDetail(SQLModel):
    id: UUID
    username_voucher: str
    password_voucher: str
    generated_at: datetime
    activated_at: Optional[datetime]
    iser_id : Optional[UUID]
    package_id: Optional[UUID] 
