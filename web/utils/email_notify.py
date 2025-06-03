import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email_notification(subject, body_text, body_html=None):
    smtp_server = os.getenv("EMAIL_SMTP_SERVER")
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER")

    if not all([smtp_server, smtp_port, sender_email, sender_password, receiver_email]):
        print("[ERRO] Variáveis de ambiente para email não estão completas.")
        return

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content(body_text)

        if body_html:
            msg.add_alternative(body_html, subtype='html')

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("[INFO] Email enviado com sucesso.")

    except Exception as e:
        print("[ERRO] Falha ao enviar email:", e)
