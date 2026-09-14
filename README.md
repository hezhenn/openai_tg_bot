# Telegram ChatGPT Bot

A versatile Telegram bot that integrates with OpenAI's ChatGPT to provide various interactive features.

---

### ✔ Core Features:

- **AI Assistant** - Tool-calling agent powered by LangChain (weather forecasts, live currency exchange & conversion)
- **ChatGPT Interface** - Direct chat with OpenAI's ChatGPT
- **Random Fact Generator** - Get interesting facts with AI-generated content
- **Celebrity Chat** - Chat with AI personalities
- **Translator** - Multi-language translation
- **Recommendations** - Content recommendations from ChatGPT

---

### ✔ Prerequisites

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Required Python packages (see `requirements.txt`)

---

### ✔ Installation

Clone the repository:

```
git clone <repository-url>
cd open_ai_telegram_bot
```

Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root and add your tokens:

```
TG_BOT_TOKEN=your_telegram_bot_token
CHATGPT_TOKEN=your_openai_api_key
```

---

### ✔ Usage

Start the bot:

```bash
python src/bot.py
```

In Telegram, find your bot using the username you set up and start a chat.

Available commands:

- `/start` - Start the bot
- `/random` - Get a random fact
- `/gpt` - Chat with ChatGPT
- `/assistant` - AI Assistant with tools (weather, currency converter)
- `/talk` - Chat with a celebrity personality
- `/translate` - Translator
- `/recommendation` - Recommendation from ChatGPT

---

### ✔ Project Structure

```
open_ai_telegram_bot
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore file
├── README.md            # This file
├── requirements.txt     # Project dependencies
└── src/
    ├── bot.py           # Main bot application
    ├── config.py        # Configuration settings
    ├── gpt.py           # GPT integration module
    ├── agent.py         # LangChain tool-calling AI assistant
    ├── handlers.py      # Bot command handlers
    ├── utils.py         # Utility functions
    └── resources/       # Resource files
        ├── images/      # Image assets for the bot
        │   ├── assistant.jpg
        │   ├── gpt.jpg
        │   ├── random.jpg
        │   ├── recommendation.jpg
        │   ├── start.jpg
        │   ├── talk.jpg
        │   ├── talk_guido_van_rossum.jpg
        │   ├── talk_linus_torvalds.jpg
        │   ├── talk_mark_zuckerberg.jpg
        │   └── translate.jpg
        ├── messages/    # Message templates
        │   └── start.txt
        └── prompts/     # AI prompt templates
            ├── assistant.txt
            ├── gpt.txt
            ├── random.txt
            ├── recommendation.txt
            ├── recommendation_dislike.txt
            ├── talk_guido_van_rossum.txt
            ├── talk_linus_torvalds.txt
            ├── talk_mark_zuckerberg.txt
            └── translate.txt
```

---

### ✔ Environment Variables

The following environment variables need to be set:

- `TG_BOT_TOKEN` (або `TELEGRAM_BOT_TOKEN`, `BOT_TOKEN`): Your Telegram Bot Token from @BotFather
- `CHATGPT_TOKEN` (або `OPENAI_API_KEY`): Your OpenAI API key
- `PROXY_URL` (optional): Proxy URL for OpenAI API if required (e.g., `http://username:password@host:port`)

---

### ✔ Contributing

- Fork the repository
- Create a new branch for your feature
- Commit your changes
- Push to the branch
- Create a new Pull Request

---

### ✔ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
