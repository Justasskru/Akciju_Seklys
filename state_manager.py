import json
import os

STATE_FILE = "state.json"

def uzkrauti_busena():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def issaugoti_busena(busena: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(busena, f, ensure_ascii=False, indent=2)