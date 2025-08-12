import uuid
from base64 import b64encode
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from config import config 
from models import Package # Assurez-vous que ce module contient vos configurations

# --------- Constantes ---------
BASE_URL = "https://sandbox.momodeveloper.mtn.com"
TOKEN_URL = f"{BASE_URL}/collection/token/"
REQUEST_TO_PAY_URL = f"{BASE_URL}/collection/v1_0/requesttopay"
CALLBACK_PATH = "/callback"
CALLBACK_URL = f"{config.callback_host}{CALLBACK_PATH}"


# --------- Fonction pour obtenir un token d'accès ---------
def get_access_token():
    try:
        auth_string = f"{config.api_user}:{config.api_key}"
        encoded_auth = b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Ocp-Apim-Subscription-Key": config.subscription_key,
            "Content-Type": "application/json"
        }
        response = requests.post(TOKEN_URL, headers=headers)
        response.raise_for_status()
        token = response.json()['access_token']
        print("[INFO] Token obtenu avec succès")
        return token

    except requests.exceptions.HTTPError as e:
        print(f"[ERREUR] HTTP lors de l'obtention du token: {e} ")
    except Exception as e:
        print(f"[ERREUR] Erreur inconnue lors de l'obtention du token: {e}")
    return None

# --------- Fonction pour envoyer une demande de paiement ---------
def request_to_pay(token, amount, payer_number, currency="EUR", external_id=None, callback_url=None):
    if external_id is None:
        external_id = str(uuid.uuid4())  

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Reference-Id": external_id,
        "X-Target-Environment": config.target_environment,
        "Ocp-Apim-Subscription-Key": config.subscription_key,
        "Content-Type": "application/json"
    }
    if callback_url:
        headers["X-Callback-Url"] = callback_url

    body = {
        "amount": amount,
        "currency": currency,
        "externalId": external_id,
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": payer_number
        },
        "payerMessage": "Paiement Zone Wifi",
        "payeeNote": "Merci pour votre paiement"
    }

    try:
        response = requests.post(REQUEST_TO_PAY_URL, json=body, headers=headers)
        if response.status_code == 202:
            print(f"[INFO] Demande de paiement acceptée (Réf: {external_id})")
            return external_id
        else:
            print(f"[ERREUR] Demande de paiement rejetée ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception lors de la demande de paiement: {e}")
    return None

# --------- Fonction pour vérifier le statut du paiement ---------
def check_payment_status(token, reference_id):
    url = f"{REQUEST_TO_PAY_URL}/{reference_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Ocp-Apim-Subscription-Key": config.subscription_key,
        "X-Target-Environment": config.target_environment,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "UNKNOWN")
            print(f"[INFO] Statut du paiement {reference_id} : {status}")
            return status
        elif response.status_code == 404:
            print(f"[ERREUR] Référence {reference_id} non trouvée (404).")
        else:
            print(f"[ERREUR] Erreur lors de la vérification du statut ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception lors de la vérification du statut: {e}")
    return None

# --------- Point d'entrée ---------
if __name__ == "__main__":
    import uvicorn

    token = get_access_token()
    if not token:
        print("[FATAL] Impossible d'obtenir le token, arrêt.")
        exit(1)

    payer_number = "46733123453"  # Exemple de numéro en format international
    amount = "5.00"

    reference_id = request_to_pay(token, amount, payer_number, callback_url=CALLBACK_URL)
    if not reference_id:
        print("[FATAL] La demande de paiement a échoué, arrêt.")
        exit(1)

    print(f"Serveur callback en écoute sur {CALLBACK_URL}")
    uvicorn.run(app, host="0.0.0.0", port=5000)