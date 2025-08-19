import smtplib
from email.mime.text import MIMEText
from config import AppConfig
from pydantic import EmailStr


def send_payment_confirmation_email(to_email:str , amount: float, txid: str | None):
   

    subject = "Confirmation de paiement"
    body = f"Votre paiement de {amount} XOF (transaction: {txid}) a été confirmé. Merci !"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = AppConfig.smtp_from_email
    msg["To"] = to_email

    with smtplib.SMTP(AppConfig.smtp_server, AppConfig.smtp_port) as server:
        server.starttls()
        server.login(AppConfig.smtp_user, AppConfig.smtp_password)
        server.send_message(msg)