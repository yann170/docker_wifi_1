from cinetpay_sdk.s_d_k import Cinetpay
from crud.transaction import update_transaction_status, get_transaction_by_txid
from config import config
from sqlmodel import Session      
from cinetpay_sdk.s_d_k import Cinetpay
from crud.transaction import update_transaction_status, get_transaction_by_txid
from config import config
from typing import Any

client = Cinetpay(apikey=config.apikey, site_id=config.side_id)


def initialize_payment(data: dict) -> Any:
    try:
        response = client.PaymentInitialization(data)
        return response
    except Exception as e:
        # log si besoin
        return {"status": "error", "message": str(e)}

def verify_transaction(transaction_id: str, session: Session) -> bool:
    
    try:
        response = client.TransactionVerfication_trx(transaction_id)

        if not response:
            return False

        tx = get_transaction_by_txid(session, transaction_id)
        if not tx:
            return False                 

    except Exception as e:
        # log si besoin
        return False
    if response.get('code') == '00' and tx.payment_gateway_ref !=None:
        update_transaction_status(
        session=session,
        transaction_id=tx.payment_gateway_ref 
        ,  # utiliser le txid externe
        new_status='SUCCESS',
        method=None  # ou passer la méthode si dispo
    )
    return True
   