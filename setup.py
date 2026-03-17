import os

from dotenv import load_dotenv

load_dotenv()

MAX_TOKEN = os.getenv("MAX_TOKEN")
MAX_CHAT_ID = int(os.getenv("MAX_CHAT_ID"))
MAX_API_URL = "https://platform-api.max.ru"

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = int(os.getenv("TG_CHAT_ID"))
