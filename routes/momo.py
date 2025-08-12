from fastapi import APIRouter, Depends
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

router = APIRouter(prefix="/momo", tags=["MoMo Payments"])

# --------- Endpoint FastAPI pour recevoir le callback MoMo ---------
CALLBACK_PATH = "/callback"
@router.post(CALLBACK_PATH)
async def callback(request: Request):
    try:
        data = await request.json()
        print(f"[CALLBACK] Callback reçu: {data}")

        # Traite ici ta logique, ex : maj base, notification, etc.
        status = data.get("status")
        reference_id = data.get("referenceId")

        print(f"Transaction {reference_id} a un statut: {status}")

        return JSONResponse(content={"message": "Callback reçu"}, status_code=200)

    except Exception as e:
        print(f"[CALLBACK ERREUR] Exception dans le callback: {e}")
        raise HTTPException(status_code=500, detail="Erreur dans le traitement du callback")
