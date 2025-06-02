import os
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def send_discord_notification(message):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("⚠️ Webhook URL não definido nas variáveis de ambiente.")
        return

    data = {
        "content": message
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            print("[WARN] Discord webhook falhou:", response.text)
        else:
            print("[INFO] Notificação enviada com sucesso.")
    except Exception as e:
        print("[ERRO] Falha ao enviar notificação Discord:", e)
