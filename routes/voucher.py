from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated, List, Optional
from uuid import UUID
from database import get_session
from models import Voucher
from schema.voucher import VoucherCreate, VoucherReadSimple, VoucherReadDetail
from datetime import datetime

router = APIRouter(prefix="/vouchers", tags=["Vouchers"])

# ------------------------
# Create voucher
# ------------------------
@router.post("/add/", response_model=VoucherReadDetail)
async def create_voucher(voucher: VoucherCreate, session: Session = Depends(get_session)):
    db_voucher = Voucher.model_validate(voucher)
    session.add(db_voucher)
    session.commit()
    session.refresh(db_voucher)
    return db_voucher

# ------------------------
# Read all vouchers (simple)
# ------------------------
@router.get("/get_all/", response_model=List[VoucherReadSimple])
async def read_vouchers(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    vouchers = session.exec(select(Voucher).offset(offset).limit(limit)).all()
    return vouchers

# ------------------------
# Read voucher by ID (detail)
# ------------------------
@router.get("/get/{voucher_id}", response_model=VoucherReadDetail)
def read_voucher(voucher_id: UUID, session: Session = Depends(get_session)):
    voucher = session.get(Voucher, voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher

# ------------------------
# Update voucher (ex: activated_at)
# ------------------------
@router.patch("/update/{voucher_id}", response_model=VoucherReadDetail)
def update_voucher(voucher_id: UUID, activated_at: Optional[datetime] = None, session: Session = Depends(get_session)):
    voucher_db = session.get(Voucher, voucher_id)
    if not voucher_db:
        raise HTTPException(status_code=404, detail="Voucher not found")
    if activated_at:
        voucher_db.activated_at = activated_at
    session.add(voucher_db)
    session.commit()
    session.refresh(voucher_db)
    return voucher_db

# ------------------------
# Delete voucher
# ------------------------
@router.delete("/delete/{voucher_id}")
def delete_voucher(voucher_id: UUID, session: Session = Depends(get_session)):
    voucher_db = session.get(Voucher, voucher_id)
    if not voucher_db:
        raise HTTPException(status_code=404, detail="Voucher not found")
    session.delete(voucher_db)
    session.commit()
    return {"ok": True}
