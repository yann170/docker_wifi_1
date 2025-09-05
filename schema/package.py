from typing import Optional, List
from sqlmodel import SQLModel
from uuid import UUID, uuid4
from schema.voucher import VoucherReadSimple
from schema.transaction import TransactionReadSimple
from pydantic import EmailStr


class PackageReadSimple(SQLModel):
    id: UUID
    name : Optional[ str]
    price: float 
    validity_hours: float
    mikrotik_profile_name: Optional[str] = None
    is_synced: bool = False
    speed_limit: float = 1.0
    #quantity_mbps:Optional[int]
    #period : Optional[str]



class PackageBase(SQLModel):
    name: str
    price: float
    validity_hours: Optional[float]
    mikrotik_profile_name: Optional[str] 
    #is_synced: bool = False
    speed_limit: float = 1.0
    #quantity_mbps: Optional[int]
    #period: Optional[str]
   

class PackageCreate(PackageBase):
    pass

class PackageUpdate(SQLModel):
    name: Optional[str] = None
    price: Optional[float] = None
    validity_hours: Optional[float] = None
    speed_limit: Optional[float] = None
    mikrotik_profile_name : Optional[str] = None



class PackageRead(PackageBase):
    id: UUID

   
class PackageReadDetail(PackageRead):
    vouchers: List[VoucherReadSimple] = []
    transactions: List[TransactionReadSimple] = []
