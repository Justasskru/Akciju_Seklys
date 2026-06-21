import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def siusti_telegram(zinute: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Trūksta TELEGRAM_TOKEN arba TELEGRAM_CHAT_ID .env faile")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": zinute
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Nepavyko išsiųsti žinutės į Telegram: {e}")
        return False