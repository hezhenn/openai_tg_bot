import logging
from random import choice

from telegram import Update
from telegram.ext import ContextTypes

from config import CHATGPT_TOKEN
from gpt import ChatGPTService
from utils import (send_image, send_text, load_message, show_main_menu, load_prompt, send_text_buttons)
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

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
            'start': 'Головне меню',
            'random': 'Дізнатися випадковий факт',
            'gpt': 'Запитати ChatGPT',
            'talk': 'Діалог з відомою особистістю',
            'translate': 'Перекладач',
            'recommendation': 'Рекомендація від ChatGPT',
        }
    )


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, "random")
    message_to_delete = await send_text(update, context, "Шукаю випадковий факт ...")
    try:
        prompt = load_prompt("random")
        fact = await chatgpt_service.send_question(
            prompt_text=prompt,
            message_text="Розкажи про випадковий факт"
        )
        buttons = {
            'random': 'Хочу ще один факт',
            'start': 'Закінчити'
        }
        await send_text_buttons(update, context, fact, buttons)
    except Exception as e:
        logger.error(f"Помилка в обробнику /random: {e}")
        await send_text(update, context, "Помилка при отриманні випадкового факту.")
    finally:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=message_to_delete.message_id
        )


async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'random':
        await random(update, context)
    elif data == 'start':
        await start(update, context)


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await send_image(update, context, "gpt")
    chatgpt_service.set_prompt(load_prompt("gpt"))
    await send_text(update, context, "Задайте питання ...")
    context.user_data["conversation_state"] = "gpt"


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    conversation_state = context.user_data.get("conversation_state")

    if conversation_state == "translate":
        print(f"DEBUG: Calling translate_text handler")  # Додайте для дебагу
        await translate_text(update, context)
        return

    if conversation_state == "recommendation":
        print(f"DEBUG: Calling rec_generate handler")  # Додайте для дебагу
        await rec_generate(update, context)
        return

    if conversation_state == "gpt":
        waiting_message = await send_text(update, context, "...")
        try:
            response = await chatgpt_service.add_message(message_text)
            await send_text(update, context, response)
        except Exception as e:
            logger.error(f"Помилка при отриманні відповіді від ChatGPT: {e}")
            await send_text(update, context, "Виникла помилка при обробці вашого повідомлення.")
        finally:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )
    if conversation_state == "talk":
        personality = context.user_data.get("selected_personality")
        if personality:
            prompt = load_prompt(personality)
            chatgpt_service.set_prompt(prompt)
        else:
            await send_text(update, context, "Спочатку оберіть особистість для розмови!")
            return
        waiting_message = await send_text(update, context, "...")
        try:
            response = await chatgpt_service.add_message(message_text)
            buttons = {"start": "Закінчити"}
            personality_name = personality.replace("talk_", "").replace("_", " ").title()
            await send_text_buttons(update, context, f"{personality_name}: {response}", buttons)
        except Exception as e:
            logger.error(f"Помилка при отриманні відповіді від ChatGPT: {e}")
            await send_text(update, context, "Виникла помилка при отриманні відповіді!")
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=waiting_message.message_id)
        finally:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )
    if not conversation_state:
        intent_recognized = await inter_random_input(update, context, message_text)
        if not intent_recognized:
            await show_funny_response(update, context)
        return


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await send_image(update, context, "talk")
    personalities = {
        'talk_linus_torvalds': "Linus Torvalds (Linux, Git)",
        'talk_guido_van_rossum': "Guido van Rossum (Python)",
        'talk_mark_zuckerberg': "Mark Zuckerberg (Meta, Facebook)",
        'start': "Закінчити",
    }
    await send_text_buttons(update, context, "Оберіть особистість для спілкування ...", personalities)


async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "start":
        context.user_data.pop("conversation_state", None)
        context.user_data.pop("selected_personality", None)
        await start(update, context)
        return
    if data.startswith("talk_"):
        context.user_data.clear()
        context.user_data["selected_personality"] = data
        context.user_data["conversation_state"] = "talk"
        prompt = load_prompt(data)
        chatgpt_service.set_prompt(prompt)
        personality_name = data.replace("talk_", "").replace("_", " ").title()
        await send_image(update, context, data)
        buttons = {'start': "Закінчити"}
        await send_text_buttons(
            update,
            context,
            f"Hello, I`m {personality_name}."
            f"\nI heard you wanted to ask me something. "
            f"\nYou can ask questions in your native language.",
            buttons
        )


async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["mode"] = "translate"

    await send_image(update, context, "translate")

    buttons = {
        "translate_ua": "🇺🇦 Українська",
        "translate_en": "🇬🇧 English",
        "translate_pl": "🇵🇱 Polski",
        "translate_de": "🇩🇪 Deutsch",
        "translate_fr": "🇫🇷 Français",
        "translate_es": "🇪🇸 Español",
        "start": "Закінчити"
    }

    await send_text_buttons(
        update, context,
        "Оберіть мову перекладу:",
        buttons
    )


async def translate_choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await start(update, context)
        return

    if query.data.startswith("translate_"):
        lang = query.data.replace("translate_", "")
        context.user_data["translate_lang"] = lang
        context.user_data["conversation_state"] = "translate"

        lang_names = {
            "ua": "українську",
            "en": "англійську",
            "pl": "польську",
            "de": "німецьку",
            "fr": "французьку",
            "es": "іспанську"
        }

        await send_text(
            update, context,
            f"Обрано переклад на {lang_names.get(lang, lang)}.\n"
            f"Надішліть текст для перекладу:"
        )


async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("conversation_state") != "translate":
        print(f"DEBUG: Not in translate state, current state: {context.user_data.get('conversation_state')}")
        return

    lang = context.user_data.get("translate_lang")
    if not lang:
        await send_text(update, context, "Спочатку оберіть мову перекладу")
        return

    text = update.message.text.strip()
    if not text:
        await send_text(update, context, "Будь ласка, введіть текст для перекладу")
        return

    print(f"DEBUG: Translating text to {lang}: {text[:50]}...")  # Додайте для дебагу

    waiting_message = await send_text(update, context, "Перекладаю...")

    try:
        prompt = load_prompt("translate")
        if not prompt:
            prompt = f"Перекладіть наступний текст на мову {lang}. Переклад має бути точним та природнім. Текст: {{text}}"

        formatted_prompt = prompt.replace("{{language}}", lang).replace("{{text}}", text)
        translation = await chatgpt_service.send_question(
            prompt_text=formatted_prompt,
            message_text=f"Переклад на {lang}: {text}"
        )

        print(f"DEBUG: Received translation: {translation[:50]}...")  # Додайте для дебагу

        buttons = {
            "translate": "Змінити мову",
            "start": "Головне меню"
        }

        await send_text_buttons(
            update, context,
            f"Переклад:\n\n{translation}\n\n"
            f"Оригінал: {text}",
            buttons
        )

        # Очищаємо стан після успішного перекладу
        context.user_data["conversation_state"] = None

    except Exception as e:
        logger.error(f"Помилка перекладу: {e}")
        await send_text(update, context, "Виникла помилка при перекладі. Спробуйте ще раз.")
    finally:
        if 'waiting_message' in locals():
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )

async def translate_callback_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "start":
        await start(update, context)
    elif data == "translate":
        await translate(update, context)
    elif data.startswith("translate_"):
        await translate_choose_lang(update, context)

async def recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["mode"] = "recommendation"

    await send_image(update, context, "recommendation")

    buttons = {
        "rec_movies": "Фільми",
        "rec_books": "Книги",
        "rec_music": "Музика",
        "rec_games": "Ігри",
        "rec_series": "Серіали",
        "start": "Головне меню"
    }

    await send_text_buttons(
        update, context,
        "Обери категорію рекомендацій:",
        buttons
    )


async def rec_choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await start(update, context)
        return

    if query.data.startswith("rec_"):
        category = query.data.replace("rec_", "")
        context.user_data["category"] = category
        context.user_data["conversation_state"] = "recommendation"

        category_names = {
            "movies": "фільмів",
            "books": "книг",
            "music": "музики",
            "games": "ігор",
            "series": "серіалів"
        }

        await send_text(
            update, context,
            f"Обрано категорію: {category_names.get(category, category)}\n"
            f"Введіть жанр або тему (наприклад: 'фантастика', 'детектив', 'рок-музика'):"
        )


async def rec_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("conversation_state") != "recommendation":
        return

    genre = update.message.text.strip()
    if not genre:
        await send_text(update, context, "Будь ласка, введіть жанр")
        return

    category = context.user_data.get("category")
    if not category:
        await send_text(update, context, "Спочатку оберіть категорію")
        return

    context.user_data["genre"] = genre
    context.user_data["attempt"] = 1

    waiting_message = await send_text(update, context, f"🔍 Шукаю рекомендацію...")

    try:
        prompt = load_prompt("recommendation")
        if not prompt:
            prompt = "Рекомендуй {{category}} у жанрі {{genre}}. Надай детальний опис, поясни чому це варто переглянути/прочитати/послухати. Форматуй відповідь зрозуміло."

        category_english = {
            "movies": "movies",
            "books": "books",
            "music": "music"
        }.get(category, category)

        formatted_prompt = prompt.replace("{{category}}", category_english).replace("{{genre}}", genre)

        recommendation_text = await chatgpt_service.send_question(
            prompt_text=formatted_prompt,
            message_text=f"Recommendation for {category} in genre {genre}"
        )

        category_ukrainian = {
            "movies": "фільмів",
            "books": "книг",
            "music": "музики"
        }.get(category, category)

        buttons = {
            "rec_dislike": "Не подобається",
            "start": "Головне меню"
        }

        await send_text_buttons(
            update, context,
            f"Рекомендація #{context.user_data['attempt']}\n"
            f"Категорія: {category_ukrainian}\n"
            f"Жанр: {genre}\n\n"
            f"{recommendation_text}",
            buttons
        )

    except Exception as e:
        logger.error(f"Помилка генерації рекомендації: {e}")

        buttons = {
            "recommendation": "Спробувати знову",
            "start": "Головне меню"
        }

        await send_text_buttons(
            update, context,
            f"Виникла помилка при генерації рекомендації.\n"
            f"Категорія: {category}\n"
            f"Жанр: {genre}\n\n"
            f"Помилка: {str(e)[:100]}...",
            buttons
        )
    finally:
        if 'waiting_message' in locals():
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )

async def rec_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    category = context.user_data.get("category")
    genre = context.user_data.get("genre")

    if not category or not genre:
        await query.edit_message_text("Спочатку оберіть категорію та жанр")
        return

    await query.edit_message_text(text="Шукаю іншу рекомендацію...")

    try:
        prompt = load_prompt("recommendation")
        if not prompt:
            prompt = "Попередня рекомендація не сподобалась. Запропонуй інші {{category}} у жанрі {{genre}}, але абсолютно інші. Надай детальний опис."

        category_english = {
            "movies": "movies",
            "books": "books",
            "music": "music"
        }.get(category, category)

        formatted_prompt = prompt.replace("{{category}}", category_english).replace("{{genre}}", genre)

        print(f"DEBUG: Sending dislike request to ChatGPT: {formatted_prompt[:200]}...")

        recommendation_text = await chatgpt_service.send_question(
            prompt_text=formatted_prompt,
            message_text=f"Another recommendation for {category} in genre {genre}"
        )

        context.user_data["attempt"] = context.user_data.get("attempt", 0) + 1

        category_ukrainian = {
            "movies": "фільмів",
            "books": "книг",
            "music": "музики"
        }.get(category, category)


        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Не подобається", callback_data="rec_dislike")],
            [InlineKeyboardButton("Головне меню", callback_data="start")]
        ])

        await query.edit_message_text(
            text=f"Нова рекомендація #{context.user_data['attempt']}\n"
                 f"Категорія: {category_ukrainian}\n"
                 f"Жанр: {genre}\n\n"
                 f"{recommendation_text}",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Помилка нової рекомендації: {e}")
        print(f"ERROR in rec_dislike: {e}")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Не подобається", callback_data="rec_dislike")],
            [InlineKeyboardButton("Головне меню", callback_data="start")]
        ])

        await query.edit_message_text(
            text=f"Виникла помилка при генерації нової рекомендації.\n\n"
                 f"Спробуйте:\n"
                 f"1. Перезапустити команду /recommendation\n"
                 f"2. Спробувати інший жанр\n"
                 f"3. Зачекати деякий час",
            reply_markup=keyboard
        )

async def inter_random_input(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    message_text_lower = message_text.lower()
    if any(keyword in message_text_lower for keyword in ['факт', 'цікав', 'random', 'випадков']):
        await send_text(
            update,
            context,
            text="Схоже, ви цікавитесь випадковими фактами! Зараз покажу вам один..."
        )
        await random(update, context)
        return True

    elif any(keyword in message_text_lower for keyword in ['gpt', 'чат', 'питання', 'запита', 'дізнатися']):
        await send_text(
            update,
            context,
            text="Схоже, у вас є питання! Переходимо до режиму спілкування з ChatGPT..."
        )
        await gpt(update, context)
        return True

    elif any(keyword in message_text_lower for keyword in ['розмов', 'говори', 'спілкува', 'особист', 'talk']):
        await send_text(
            update,
            context,
            text="Схоже, ви хочете поговорити з відомою особистістю! Зараз покажу вам доступні варіанти..."
        )
        await talk(update, context)
        return True
    return False

async def recommendation_callback_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "start":
        await start(update, context)
    elif data.startswith("rec_"):
        if data == "rec_dislike":
            await rec_dislike(update, context)
        else:
            await rec_choose_category(update, context)

async def show_funny_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    funny_responses = [
        "Хмм... Цікаво, але я не зрозумів, що саме ви хочете. Може спробуєте одну з команд з меню?",
        "Дуже цікаве повідомлення! Але мені потрібні чіткіші інструкції. Ось доступні команди:",
        "Ой, здається, ви мене застали зненацька! Я вмію багато чого, але мені потрібна конкретна команда:",
        "Вибачте, мої алгоритми не розпізнали це як команду. Ось що я точно вмію:",
        "Це повідомлення таке ж загадкове, як єдиноріг у дикій природі! Спробуйте одну з цих команд:",
        "Я намагаюся зрозуміти ваше повідомлення... Але краще скористайтесь однією з команд:",
        "О! Випадкове повідомлення! Я теж вмію бути випадковим, але краще використовуйте команди:",
        "Гм, не спрацювало. Може спробуємо ці команди?",
        "Це повідомлення прекрасне, як веселка! Але для повноцінного спілкування спробуйте:",
        "Згідно з моїми розрахунками, це повідомлення не відповідає жодній з моїх команд. Ось вони:",
    ]
    random_response = choice(funny_responses)
    available_commands = """
    - Не знаєте, що обрати? Почніть з /start,
    - Спробуйте команду /gpt, щоб задати питання,
    """
    full_message = f"{random_response}\n{available_commands}"
    await update.message.reply_text(full_message)


