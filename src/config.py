import os
from dotenv import load_dotenv

load_dotenv()

CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN") or os.getenv("OPENAI_API_KEY")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("PROXY_URL") or os.getenv("OPENAI_PROXY")


