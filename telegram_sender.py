import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def siusti_telegram(zinute: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Trūksta TELEGRAM_TOKEN arba TELEGRAM_CHAT_ID .env faile")
        return False

    url = f"{BASE_URL}/sendMessage"
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


from typing import Optional

def gauti_paskutine_komanda(offset: Optional[int] = None):
    """
    Grąžina: (komanda, update_id) arba (None, None)
    """
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 1}
    if offset is not None:
        params["offset"] = offset

    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        if not data.get("ok"):
            return None, None

        results = data.get("result", [])
        if not results:
            return None, None

        paskutinis = results[-1]
        update_id = paskutinis.get("update_id")
        text = paskutinis.get("message", {}).get("text", "")

        return text.strip(), update_id
    except Exception as e:
        print(f"Klaida skaitant Telegram komandas: {e}")
        return None, None

def gauti_update(offset=None):
    # jei jau turi gauti_paskutine_komanda, peradresuok:
    return gauti_paskutine_komanda(offset)