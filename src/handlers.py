import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils import send_image, send_text, load_message, show_main_menu
from gpt import ChatGPTService
from src.config import CHATGPT_TOKEN

chatgpt_service = ChatGPTService(CHATGPT_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, "start")
    await send_text(update, context, load_message("start"))
    await show_main_menu(
        update,
        context,
        {
            'start': 'Main menu',
            'random': 'Learn a random fact',
            'gpt': 'Ask ChatGPT',
            'talk': 'Talk to a famous person',
            'quiz': 'Test your knowledge'
        }
    )