from cinetpay_sdk.s_d_k import Cinetpay
from crud.transaction import update_transaction_status, get_transaction_by_txid
from config import config

client = Cinetpay(apikey=config.apikey, site_id=config.side_id)

def initialize_payment(data):
    # Appelle CinetPay et retourne la réponse
    return client.PaymentInitialization(data)

def verify_transaction(transaction_id: str):
    response = client.TransactionVerfication_trx(transaction_id)
    return response
