from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

from config import TG_BOT_TOKEN
from handlers import start

app = ApplicationBuilder().token(TG_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES
)