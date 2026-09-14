import logging
from typing import Optional
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

WEATHER_CODES = {
    0: "Ясне небо ☀️",
    1: "Переважно ясно 🌤",
    2: "Мінлива хмарність ⛅",
    3: "Похмуро ☁️",
    45: "Туман 🌫",
    48: "Паморозь 🌫",
    51: "Легка мряка 🌧",
    53: "Помірна мряка 🌧",
    55: "Густа мряка 🌧",
    61: "Невеликий дощ 🌦",
    63: "Помірний дощ 🌧",
    65: "Сильний дощ 🌧🌧",
    71: "Невеликий сніг 🌨",
    73: "Помірний сніг 🌨",
    75: "Сильний снігопад ❄️",
    77: "Снігова крупа ❄️",
    80: "Короткочасні дощі 🌦",
    81: "Зливовий дощ 🌧",
    82: "Сильна злива ⛈",
    85: "Невеликий снігопад 🌨",
    86: "Сильний снігопад ❄️",
    95: "Гроза ⚡",
    96: "Гроза з градом ⛈",
    99: "Сильна гроза з градом ⛈"
}


@tool
def get_weather(city: str) -> str:
    """Отримати поточну інформацію про погоду для вказаного міста (наприклад: 'Київ', 'Львів', 'Варшава', 'London').
    Аргумент:
        city: назва міста будь-якою мовою.
    """
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = httpx.get(geo_url, params={"name": city, "count": 1, "language": "uk"}, timeout=10)
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return f"Місто '{city}' не знайдено. Перевірте правильність написання назви."

        loc = geo_data["results"][0]
        lat = loc["latitude"]
        lon = loc["longitude"]
        city_name = loc.get("name", city)
        country = loc.get("country", "")

        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        w_resp = httpx.get(weather_url, params=params, timeout=10)
        curr = w_resp.json().get("current", {})
        temp = curr.get("temperature_2m")
        apparent = curr.get("apparent_temperature")
        humidity = curr.get("relative_humidity_2m")
        wind = curr.get("wind_speed_10m")
        code = curr.get("weather_code", 0)
        desc = WEATHER_CODES.get(code, f"Код погоди {code}")

        return (
            f"Погода у {city_name} ({country}):\n"
            f"- Температура: {temp}°C (відчувається як {apparent}°C)\n"
            f"- Стан: {desc}\n"
            f"- Вологість: {humidity}%\n"
            f"- Швидкість вітру: {wind} км/год"
        )
    except Exception as e:
        logger.error(f"Помилка отримання погоди для '{city}': {e}")
        return f"Не вдалося отримати прогноз погоди через помилку: {e}"


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Конвертувати суму з однієї валюти в іншу або дізнатися актуальний курс обміну валют.
    Аргументи:
        amount: числове значення суми (наприклад 100 або 1).
        from_currency: назва або 3-значний код вихідної валюти (наприклад: 'USD', 'долар', 'EUR', 'євро', 'UAH', 'гривня', 'PLN', 'злотий').
        to_currency: назва або 3-значний код цільової валюти (наприклад: 'UAH', 'гривня', 'USD', 'EUR').
    """
    aliases = {
        "долар": "USD", "долари": "USD", "доларів": "USD", "дол": "USD", "$": "USD", "usd": "USD",
        "євро": "EUR", "евро": "EUR", "€": "EUR", "eur": "EUR",
        "гривня": "UAH", "гривні": "UAH", "гривень": "UAH", "грн": "UAH", "₴": "UAH", "uah": "UAH",
        "злотий": "PLN", "злоті": "PLN", "злотих": "PLN", "pln": "PLN",
        "фунт": "GBP", "фунти": "GBP", "фунтів": "GBP", "£": "GBP", "gbp": "GBP",
        "єна": "JPY", "йєна": "JPY", "jpy": "JPY",
        "франк": "CHF", "chf": "CHF",
    }
    base = aliases.get(from_currency.strip().lower(), from_currency.strip().upper())
    target = aliases.get(to_currency.strip().lower(), to_currency.strip().upper())

    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        resp = httpx.get(url, timeout=10)
        data = resp.json()
        if data.get("result") != "success":
            return f"Не вдалося отримати дані для валюти '{base}'. Перевірте назву або код валюти."

        rate = data.get("rates", {}).get(target)
        if rate is None:
            return f"Курс для цільової валюти '{target}' відносно '{base}' не знайдено."

        converted = amount * rate
        return f"{amount:g} {base} = {converted:.2f} {target} (Курс: 1 {base} = {rate:.4f} {target})"
    except Exception as e:
        logger.error(f"Помилка конвертації валют {from_currency} -> {to_currency}: {e}")
        return f"Не вдалося виконати конвертацію через помилку: {e}"


class AIAssistantService:
    def __init__(self, token: str, proxy: Optional[str] = "http://18.199.183.77:49232"):
        http_client = httpx.AsyncClient(proxy=proxy) if proxy else None
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=token,
            temperature=0.7,
            http_async_client=http_client
        )
        self.tools = [get_weather, convert_currency]
        self.checkpointer = MemorySaver()
        self.system_prompt = (
            "Ти — розумний, ввічливий та помічний AI-асистент у Telegram.\n"
            "Ти допомагаєш користувачеві з різними запитаннями та маєш спеціальні інструменти:\n"
            "1. get_weather — дізнатися поточну погоду в місті.\n"
            "2. convert_currency — дізнатися курс валют або конвертувати суму.\n"
            "Якщо запитання користувача стосується погоди чи курсів/конвертації валют, обов'язково використовуй відповідний інструмент.\n"
            "Відповідай структуровано, зрозуміло та українською мовою."
        )
        self._init_agent()

    def _init_agent(self):
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer
        )

    def set_prompt(self, prompt_text: str) -> None:
        self.system_prompt = prompt_text
        self._init_agent()

    async def add_message(self, message_text: str, thread_id: str = "default") -> str:
        config = {"configurable": {"thread_id": thread_id}}
        response = await self.agent.ainvoke(
            {"messages": [("user", message_text)]},
            config=config
        )
        messages = response.get("messages", [])
        if messages:
            last_message = messages[-1]
            return last_message.content
        return "Не вдалося отримати відповідь."
