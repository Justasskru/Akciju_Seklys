import json
import os
import signal
import subprocess
import sys

BOT_STATUS_FILE = "bot_status.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PATH = os.path.join(BASE_DIR, "main.py")

def _default_status():
    return {"running": False, "pid": None}

def load_bot_status():
    if not os.path.exists(BOT_STATUS_FILE):
        data = _default_status()
        save_bot_status(data)
        return data
    try:
        with open(BOT_STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        data = _default_status()
        save_bot_status(data)
        return data

def save_bot_status(data):
    with open(BOT_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_pid_running(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False

def start_bot():
    status = load_bot_status()
    pid = status.get("pid")

    if status.get("running") and is_pid_running(pid):
        return False, f"Botas jau veikia (PID: {pid})"

    if not os.path.exists(MAIN_PATH):
        return False, f"Nerastas failas: {MAIN_PATH}"

    try:
        p = subprocess.Popen(
            [sys.executable, MAIN_PATH],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        return False, f"Nepavyko paleisti boto: {e}"

    save_bot_status({"running": True, "pid": p.pid})
    return True, f"Botas paleistas (PID: {p.pid})"

def stop_bot():
    status = load_bot_status()
    pid = status.get("pid")

    if not status.get("running") or not is_pid_running(pid):
        save_bot_status({"running": False, "pid": None})
        return False, "Botas jau sustabdytas."

    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        pass

    save_bot_status({"running": False, "pid": None})
    return True, f"Botas sustabdytas (PID: {pid})"

def refresh_bot_status():
    status = load_bot_status()
    pid = status.get("pid")
    if status.get("running") and not is_pid_running(pid):
        status = {"running": False, "pid": None}
        save_bot_status(status)
    return status