import requests

def send_discord_notification(message):
    webhook_url = 'https://discord.com/api/webhooks/1376989585292398622/despYmrYYAI_kWmbKdejMNbBlnwRMtQONYOt-PjjqFmTC5DpzS8mub5KWATdnsoNcu6v'
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
