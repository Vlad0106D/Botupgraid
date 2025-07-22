import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from quart import Quart
import httpx
import numpy as np

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
PAIRS = ["bitcoin", "ethereum", "solana", "ripple"]
VS_CURRENCY = "usd"

# Настройка логов
logging.basicConfig(level=logging.INFO)
app_web = Quart(__name__)

# ===== Получение данных с CoinGecko =====
async def fetch_market_data(coin_id: str, days: int = 1, interval: str = "hourly"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": VS_CURRENCY, "days": days, "interval": interval}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            prices = [p[1] for p in data["prices"]]
            return prices
        except Exception as e:
            logging.error(f"Ошибка при получении данных {coin_id}: {e}")
            return None

# ===== Стратегия комплексного анализа =====
def analyze_strategy(prices: list) -> str:
    if len(prices) < 20:
        return "Недостаточно данных"

    prices_np = np.array(prices)

    rsi = compute_rsi(prices_np)
    momentum = prices_np[-1] - prices_np[-10]
    ma_fast = prices_np[-5:].mean()
    ma_slow = prices_np[-20:].mean()

    if rsi < 30 and momentum > 0 and ma_fast > ma_slow:
        return "LONG"
    elif rsi > 70 and momentum < 0 and ma_fast < ma_slow:
        return "SHORT"
    else:
        return "NONE"

# ===== Расчёт RSI =====
def compute_rsi(prices: np.ndarray, period: int = 14) -> float:
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.convolve(gain, np.ones(period), 'valid') / period
    avg_loss = np.convolve(loss, np.ones(period), 'valid') / period
    rs = avg_gain[-1] / avg_loss[-1] if avg_loss[-1] != 0 else 1
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ===== Команда /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Используй команду /check для анализа рынка.")

# ===== Команда /check =====
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализирую рынок...")
    messages = []

    for coin_id in PAIRS:
        prices = await fetch_market_data(coin_id)
        if prices:
            signal = analyze_strategy(prices)
            messages.append(f"{coin_id.upper()}: {signal}")
        else:
            messages.append(f"{coin_id.upper()}: ошибка загрузки данных")

    result = "\n".join(messages)
    await update.message.reply_text(result)

# ===== Запуск Telegram-бота =====
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    # Telegram-пуллинг запускаем в отдельной задаче
    loop = asyncio.get_event_loop()
    loop.create_task(app.run_polling())

    # Quart-сервер
    @app_web.route("/")
    async def home():
        return "Бот работает!"

    import hypercorn.asyncio
    config = hypercorn.Config()
    config.bind = ["0.0.0.0:10000"]
    await hypercorn.asyncio.serve(app_web, config)

# Точка входа
if __name__ == "__main__":
    asyncio.run(main())