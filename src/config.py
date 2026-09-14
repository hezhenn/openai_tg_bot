import os
from dotenv import load_dotenv

load_dotenv()

CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN") or os.getenv("OPENAI_API_KEY")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
OPENAI_PROXY = os.getenv("OPENAI_PROXY", "http://18.199.183.77:49232")

