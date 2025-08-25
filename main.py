# main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session,select
from typing import AsyncGenerator
from database import engine ,get_session, create_table_in_db
from models import User, Package, Transaction, Voucher 
from routes import package, payement,auth
from routes import user




app = FastAPI(
    title="Portail Captif MikroTik API",
    version="0.1.0",
    description="Backend pour un portail captif personnalisé avec MikroTik."
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
    allow_methods=["*"], # Autorise toutes les méthodes (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Autorise tous les en-têtes
)

@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur le backend FastAPI de votre portail MikroTik!"}

@app.post("/test-user/")
async def create_test_user(username: str, db: Session = Depends(get_session)):
    new_user = User(username=username, hashed_password="hashed_test_password")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Utilisateur de test créé avec succès!", "user_id": new_user.id}

@app.get("/users/")
async def get_all_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    return users 

app.include_router(package.router)
app.include_router(payement.router)
app.include_router(user.router)
app.include_router(auth.router)