import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def siusti_telegram(zinute):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Trūksta TELEGRAM_TOKEN arba TELEGRAM_CHAT_ID .env faile")
        return False

    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": zinute}

    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print("Nepavyko išsiųsti žinutės:", e)
        return False

def gauti_update(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 1}
    if offset is not None:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            return None, None
        results = data.get("result", [])
        if not results:
            return None, None
        last = results[-1]
        text = last.get("message", {}).get("text", "")
        update_id = last.get("update_id")
        return text, update_id
    except Exception as e:
        print("Klaida getUpdates:", e)
        return None, None