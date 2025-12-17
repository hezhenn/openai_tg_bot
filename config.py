# Імпорт необхідних бібліотек
import os
from dotenv import load_dotenv  # Для роботи з файлом .env

# Завантаження змінних середовища з файлу .env
load_dotenv()

# Отримання токена ChatGPT зі змінних середовища
CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN")
# Токен Telegram бота
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
