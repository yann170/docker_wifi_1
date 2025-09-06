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
from services.service_mikrotik.mikrotik import MikroTikProfileCreator, generate_nhr_code
from  config import config
from apps.models.models import User
from typing import Annotated
from fastapi import Security
from crud.auth import get_current_user
from crud.voucher import create_voucher
from schema.voucher import VoucherCreate
from crud.voucher import create_voucher
from schema.voucher import VoucherCreate

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

# 8.3 POST /notify → notification de paiement (webhook)
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

    # 2) Idempotence
    if tx.payment_status == "ACCEPTED":
        return {"status": "ALREADY_ACCEPTED"}

    # 3) Vérifier l’état côté CinetPay
    cp_status = verify_transaction(cpm_trans_id, session)
    if not isinstance(cp_status, dict):
        raise HTTPException(status_code=502, detail="Réponse CinetPay invalide")

    data = cp_status.get("data") or {}
    if not data:
        raise HTTPException(status_code=404, detail="Impossible d'accéder à CinetPay")

    status = data.get("status")
    method = data.get("payment_method")
    transaction_id = data.get("transaction_id")

    # 4) Mise à jour locale
    if status == "ACCEPTED":
        update_transaction_status(session, cpm_trans_id, "ACCEPTED", method=method)
          # 5) Génération du voucher MikroTik
        try:
            if not tx.package or not tx.package.mikrotik_profile_name:
                raise HTTPException(status_code=500, detail="Package ou profil MikroTik manquant")
            voucher_code = generate_nhr_code()  
            profile_name = tx.package.mikrotik_profile_name  
            mikrotik_service = MikroTikProfileCreator(host=config.mikrotik_host, username=config.mikrotik_user, password=config.mikrotik_password)
            created_voucher = mikrotik_service.create_voucher(
                code=voucher_code,
                profile_name=profile_name
            )
            # Créer un objet VoucherCreate
            voucher_data = VoucherCreate(
                username_voucher=created_voucher,           
                password_voucher=created_voucher,  # ou un mot de passe différent
                user_id=tx.user_id,
                package_id=tx.package_id
            )
            # Appeler la fonction CRUD pour enregistrer en base
            db_voucher = create_voucher(session=session, voucher_data=voucher_data)


        except HTTPException as e:
            # En cas d'erreur MikroTik, on peut logger et continuer ou renvoyer une erreur
            raise e

        # 5) Email utilisateur
        customer_email = get_email_by_transaction_id(session, cpm_trans_id)

        if customer_email:
            background_tasks.add_task(
                send_payment_confirmation_email,
                to_email=customer_email,
                amount=tx.amount_paid,  # montant attendu
                txid=tx.payment_gateway_ref,
                 voucher_code=created_voucher  
            )

        # TODO: deliver_wifi_service(user_id=tx.user_id, package_id=tx.package_id)
        return {"status": "OK", "updated": "ACCEPTED"}

    elif status == "REFUSED":
        update_transaction_status(session, cpm_trans_id, "REFUSED", method=method)
        return {"status": "OK", "updated": "REFUSED"}

    else:
        update_transaction_status(session, cpm_trans_id, status or "PENDING", method=method)
        return {"status": "OK", "updated": status or "PENDING"}

# 9. Endpoint d’activation manuelle (admin)

@router.post("/activate-forfait/{transaction_id}", tags=["payments"])
async def activate_forfait(
    transaction_id: str,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Security(get_current_user, scopes=["admin"])],
    session: Session = Depends(get_session),
):
   
    tx = get_transaction_by_txid(session, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    # Mettre à jour le statut à ACCEPTED
    update_transaction_status(session, transaction_id, "ACCEPTED", method="MANUAL")

    # Vérification du package et du profil MikroTik
    if not tx.package or not tx.package.mikrotik_profile_name:
        raise HTTPException(status_code=500, detail="Package ou profil MikroTik manquant")

    # Générer le voucher
    voucher_code = generate_nhr_code()
    mikrotik_service = MikroTikProfileCreator(
        host=config.mikrotik_host,
        username=config.mikrotik_user,
        password=config.mikrotik_password
    )
    created_voucher = mikrotik_service.create_voucher(
        code=voucher_code,
        profile_name=tx.package.mikrotik_profile_name
    )
    


# Créer un objet VoucherCreate
    voucher_data = VoucherCreate(
        username_voucher=created_voucher,
        password_voucher=created_voucher,  # ou un mot de passe différent
        user_id=tx.user_id,
        package_id=tx.package_id
    )

# Appeler la fonction CRUD pour enregistrer en base
    db_voucher = create_voucher(session=session, voucher_data=voucher_data)


    # Envoyer l'email à l'utilisateur
    customer_email = get_email_by_transaction_id(session, transaction_id)
    if customer_email:
        background_tasks.add_task(
            send_payment_confirmation_email,
            to_email=customer_email,
            amount=tx.amount_paid or 0.0,
            txid=tx.payment_gateway_ref or "MANUAL",
            voucher_code=created_voucher
        )

    return {"status": "OK", "voucher": created_voucher, "updated": "ACCEPTED"}
