from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated, List, Optional
from uuid import UUID
from database import get_session
from models import Voucher
from schema.voucher import VoucherCreate, VoucherReadSimple, VoucherReadDetail
from datetime import datetime
from crud.user import get_user_by_id
from crud.package import get_package_by_id

router = APIRouter(prefix="/vouchers", tags=["Vouchers"])

# ------------------------
# Create voucher
@router.post("/vouchers/", response_model=VoucherReadDetail)
async def create_voucher(voucher: VoucherCreate, session: Session = Depends(get_session)):
    # Vérifier que l'utilisateur existe
    if not voucher.user_id or not get_user_by_id(session, voucher.user_id):
        raise HTTPException(status_code=400, detail="Valid user_id is required")
    
    # Vérifier que le package existe
    if not voucher.package_id or not get_package_by_id(session, voucher.package_id):
        raise HTTPException(status_code=400, detail="Valid package_id is required")

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
    vouchers = session.exec(select(Voucher).where(Voucher.statut!="delete").offset(offset).limit(limit)).all()
    return vouchers

# ------------------------
# Read voucher by ID (detail)
# ------------------------
@router.get("/get/{voucher_id}", response_model=VoucherReadDetail)
def read_voucher(voucher_id: UUID, session: Session = Depends(get_session)):
    voucher = session.get(Voucher, voucher_id)
    if not voucher or voucher.statut == "delete":
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher

# ------------------------
# Update voucher (ex: activated_at)
# ------------------------
@router.patch("/update/{voucher_id}", response_model=VoucherReadDetail)
def update_voucher(voucher_id: UUID, activated_at: Optional[datetime] = None, session: Session = Depends(get_session)):
    voucher_db = session.get(Voucher, voucher_id)
    if not voucher_db or voucher_db.statut == "delete":
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
    if not voucher_db or voucher_db.statut == "delete":
        raise HTTPException(status_code=404, detail="Voucher not found")
    voucher_db.statut = "deleted"
    session.add(voucher_db)
    session.commit()
    return {"ok": True}
