# routes/payments.py
import uuid
from fastapi import APIRouter, Depends, Form, Header, BackgroundTasks
from sqlmodel import Session
from database import get_session
from crud.transaction import create_transaction, get_transaction_by_txid , get_user_email_by_user_id , update_transaction_status,get_email_by_transaction_id
from services.payement_service.cinetpay_service import initialize_payment, verify_transaction
from services.payement_service.notification_service import send_payment_confirmation_email
from uuid import UUID
from fastapi import HTTPException


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/init")
def init_payment(
    user_id: UUID,
    package_id: UUID,
    amount: float = 0.0,
    session: Session = Depends(get_session),
    payment_method: str = Form(...),  # "cinetpay" ou autre
):
    # a) Créer ton transaction_id unique (côté marchand)
    txid = f"TX-{uuid.uuid4().hex[:16]}"

    # b) Enregistrer la transaction en attente côté DB
    create_transaction(
        session,
        transaction_id=txid,
        user_id=user_id,
        amount=amount,
        package_id=package_id,
        payment_method=payment_method,
        status="PENDING",
    )
    customer_email = get_user_email_by_user_id(session, user_id)

    # c) Construire le payload pour CinetPay
    data = {
    "amount": amount,
    "currency": "XAF",  # correspond à ton compte
    "transaction_id": txid,  # identifiant unique de la transaction
    "description": "Abonnement WiFi Zone",
    "return_url": "https://ton-front.com/return",       # page front de retour
    "notify_url": "https://ton-api.com/payments/notify",# endpoint webhook pour notification
    "customer_name": "Client",
    "customer_surname": "WiFi",
    "customer_email": "client@example.com",  # obligatoire pour éviter erreur MINIMUM_REQUIRED_FIELDS
    "metadata": {                             # facultatif, mais pratique pour ton suivi
        "user_id": str(user_id),
        "package_id": str(package_id)
    },
    "channel": "MOBILE_MONEY",               # ou "CARD" selon le mode de paiement
    "payment_method": "ORANGE_MONEY"         # exemple, choisir celui accepté
}
    # d) Appel SDK → reçoit les infos pour rediriger le client
    cp_response = initialize_payment(data)

    # e) Retourner la réponse CinetPay (URL/Token) au front
    return {"transaction_id": txid, "cinetpay": cp_response, "email": customer_email}


# 8.2 GET /notify → simple ping de disponibilité (doit renvoyer 200 OK)
@router.get("/notify")
def notify_ping():
    return {"status": "OK"}


# 8.3 POST /notify → route appelée par CinetPay après chaque update
@router.post("/notify")
def notify_payment(
    background_tasks: BackgroundTasks,
    cpm_site_id: str = Form(...),     
    cpm_trans_id: str = Form(...),   
    x_token: str = Header(...),       
    session: Session = Depends(get_session)
):
    # 1) Vérifier que la transaction existe localement
    tx = get_transaction_by_txid(session, cpm_trans_id)
    if not tx:
        # Transaction inconnue → on répond 200 pour éviter les retries infinis
        return {"status": "IGNORED", "reason": "transaction not found"}

    # 2) Si déjà ACCEPTED, ne rien refaire (idempotence)
    if tx.payment_status == "ACCEPTED":
        return {"status": "ALREADY_ACCEPTED"}

    # 3) Vérifier l’état côté CinetPay (source de vérité)
    cp_status = verify_transaction(cpm_trans_id)
    # Exemple de structure attendue:
    # {"code": "00", "message": "SUCCES", "data": {"status": "ACCEPTED", ...}}

    data = cp_status.get("data") #or {}
    if data !={}:
        status = data.get("status")  # "ACCEPTED" | "REFUSED" | "PENDING" | etc.
        method = data.get("payment_method")
        transaction_id = data.get("transaction_id")

    # 4) Mettre à jour localement
        if status == "ACCEPTED" :
            update_transaction_status(session, cpm_trans_id, "ACCEPTED", method=method)

        # 5) Délivrer le service (ex: activer l'abonnement) — à toi d’implémenter
        # deliver_wifi_service(user_id=tx.user_id, package_id=tx.package_id)

        # 6) Envoi d'email en tâche de fond (non bloquant)

            background_tasks.add_task(
                send_payment_confirmation_email,
                to_email= transaction_id ,
                amount=tx.amount_paid,
                txid=tx.payment_gateway_ref,
        )

            return {"status": "OK", "updated": "ACCEPTED"}

        elif status == "REFUSED":
            update_transaction_status(session, cpm_trans_id, "REFUSED",method = method)
            return {"status": "OK", "updated": "REFUSED"}

        else:
            # WAITING_FOR_CUSTOMER ou autre → ne pas passer REFUSED trop tôt
            update_transaction_status(session, cpm_trans_id, status or "PENDING",method=method)
        return {"status": "OK", "updated": status or "PENDING"}
    else:
        raise HTTPException(status_code=404, detail = "impossible d'accéder à cinetpay ")
