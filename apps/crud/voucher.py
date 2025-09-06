from sqlmodel import Session
from apps.models.models import Voucher
from schema.voucher import VoucherCreate    

def create_voucher(
    session: Session,
    voucher_data: VoucherCreate
) -> Voucher:
    db_voucher = Voucher.model_validate(voucher_data)
    session.add(db_voucher) 
    session.commit()
    session.refresh(db_voucher)
    return db_voucher
