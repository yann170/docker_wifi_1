# models.py
from typing import Optional
from datetime import datetime, timezone 
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from pydantic import EmailStr


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str = Field()
    email: Optional[EmailStr] = Field(default=None, index=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    numero: Optional[str] = Field(default=None, index=True, unique=True)    
    vouchers: list["Voucher"] = Relationship(back_populates="user", passive_deletes="all", cascade_delete=False)
    transactions: list["Transaction"] = Relationship(back_populates="user", passive_deletes="all", cascade_delete=False)
    statut: str = Field(default="active")  
    role :  str = Field(default="user")


class Package(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    price: float = Field()
    validity_hours: int = Field()
    speed_limit: float = Field(default=1.0)
    mikrotik_profile_name: Optional[str] = Field(default=None, index=True, unique=True)
    is_synced: bool = Field(default=False)
      # True si le profil a été
    #period: Optional[str] = Field(default=None)
    #quantity_mbps: Optional[int] = Field(default=None)
    vouchers: list["Voucher"] = Relationship(back_populates="package", passive_deletes="all", cascade_delete=False)
    transactions: list["Transaction"] = Relationship(back_populates="package", passive_deletes="all", cascade_delete=False)



class Transaction(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id:UUID = Field(foreign_key="user.id", ondelete="SET NULL", nullable=True)
    package_id: UUID = Field(foreign_key="package.id", ondelete="SET NULL", nullable=True)
    amount_paid: float = Field()
    payment_method: str | None = Field(default="cash")
    payment_status: str = Field(default="pending")
    payment_gateway_ref: Optional[str] = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    user: Optional["User"] = Relationship(back_populates="transactions")
    package: Optional["Package"] = Relationship(back_populates="transactions")
    

class Voucher(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    username_voucher: str = Field(index=True, unique=True)
    password_voucher: str
    user_id: UUID | None = Field(foreign_key="user.id", ondelete="SET NULL",nullable=True)
    package_id: UUID | None = Field(foreign_key="package.id", ondelete="SET NULL",nullable=True)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    user: Optional["User"] = Relationship(back_populates="vouchers")
    package: Optional["Package"] = Relationship(back_populates="vouchers")
