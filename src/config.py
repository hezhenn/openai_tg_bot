import os
from dotenv import load_dotenv

load_dotenv()

CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
