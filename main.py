# main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session,select
from database import engine ,get_session, create_table_in_db
from routes import package, payement,auth,user,transaction,voucher
from models import User
from services.auth_service.auth import authenticate_user, create_access_token
from datetime import timedelta
from schema.auth import Token
from fastapi.security import OAuth2PasswordRequestForm  
from config import config   
from typing import Annotated
from crud.auth import get_current_user
from crud.user import get_role_by_username



app = FastAPI(
    title="Portail Captif MikroTik API",
    version="0.1.0",
    description="Backend pour un portail captif personnalisé avec MikroTik.",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    # Si votre frontend est sur MikroTik (en développement/test)
    "http://192.168.50.250", # Remplacez par l'IP de votre interface Hotspot
    "https://hotspot.mikrotik.com", # URL de redirection Hotspot
    # Si votre frontend est hébergé en ligne (ex: Netlify, Vercel)
    "https://votre-frontend-en-ligne.netlify.app", # Remplacez par votre URL réelle
    # L'URL de votre backend FastAPI sur Render (si le frontend l'appelle directement)
    "https://votre-url-fastapi.onrender.com",
    # Si vous utilisez des variables d'environnement pour l'URL du frontend
    os.getenv("FRONTEND_URL", "http://localhost:3000") # Valeur par défaut pour le dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in origins if origin], # Convertit en str et filtre les vides
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API du Portail Captif MikroTik"}

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Définir les scopes en fonction du rôle réel de l'utilisateur
    user_scopes = [get_role_by_username(session, form_data.username)]


    access_token = create_access_token(
        data={"sub": user.username, "scopes": user_scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")



app.include_router(package.router,  dependencies=[Depends(get_current_user)],)
app.include_router(payement.router,  dependencies=[Depends(get_current_user)],)
app.include_router(user.router)
app.include_router(auth.router,)
app.include_router(transaction.router)
app.include_router(voucher.router)