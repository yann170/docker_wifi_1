from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    # --- Database ---
    db_name: str
    db_user: str
    db_password: str
    database_url: str

    # --- CinetPay ---
    apikey: str
    side_id: str
    cle_secrete: str

    # --- SMTP ---
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from_email: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "forbid",
    }

# --- Créer une instance ---
config = AppConfig() # type: ignore 
