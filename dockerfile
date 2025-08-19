# Dockerfile
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer le SDK depuis GitHub
RUN pip install --no-cache-dir -i https://test.pypi.org/simple cinetpay-sdk==0.1.1

# Copier tout le reste du code de l'application
COPY . .

# Exposer le port sur lequel FastAPI va écouter
EXPOSE 8000 

# Ou 8081 si c'est le port que vous avez choisi pour FastAPI

# Commande par défaut pour lancer l'application avec Uvicorn
# On utilise 0.0.0.0 pour écouter sur toutes les interfaces, nécessaire pour Docker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]