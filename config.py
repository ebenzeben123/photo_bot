import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
JOBNIMBUS_API_KEY = os.getenv("JOBNIMBUS_API_KEY")