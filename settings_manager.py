import json
import os
from config import MANO_AKCIJOS, CHECK_INTERVAL

SETTINGS_FILE = "settings.json"

def default_settings():
    return {
        "stocks": dict(MANO_AKCIJOS),
        "check_interval": int(CHECK_INTERVAL)
    }

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        data = default_settings()
        save_settings(data)
        return data

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = default_settings()
        save_settings(data)
        return data

    if "stocks" not in data or not isinstance(data["stocks"], dict):
        data["stocks"] = dict(MANO_AKCIJOS)

    if "check_interval" not in data:
        data["check_interval"] = int(CHECK_INTERVAL)

    normalized = {}
    for k, v in data["stocks"].items():
        try:
            normalized[str(k).upper()] = float(v)
        except Exception:
            pass
    data["stocks"] = normalized

    try:
        data["check_interval"] = int(data["check_interval"])
    except Exception:
        data["check_interval"] = int(CHECK_INTERVAL)

    save_settings(data)
    return data