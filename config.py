import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "3600"))

MANO_AKCIJOS = {
    "AAPL": 245.0,
    "TSLA": 340.0,
    "MSFT": 350.0,
    "GOOGL": 300.0,
    "NVDA": 700.0,
    "AMZN": 240.0,
}