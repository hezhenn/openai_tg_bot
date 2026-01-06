from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import TG_BOT_TOKEN
from handlers import start, random, random_button, gpt, message_handler, talk, talk_button, translate, translate_choose_lang, translate_text, translate_callback_handler, recommendation, rec_choose_category, rec_generate, rec_dislike, recommendation_callback_handler

app = ApplicationBuilder().token(TG_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(CommandHandler("recommendation", recommendation))

app.add_handler(CallbackQueryHandler(translate_callback_handler, pattern="^(translate|start|translate_.*)$"))
app.add_handler(CallbackQueryHandler(recommendation_callback_handler, pattern="^(rec_.*|start)$"))
app.add_handler(CallbackQueryHandler(random_button, pattern='^(random|start)$'))
app.add_handler(CallbackQueryHandler(talk_button, pattern='^(talk_.*|start)$'))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

print("Бот запущено! Чекаю повідомлень...")
app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)