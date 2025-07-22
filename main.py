import logging
import numpy as np
import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Привет! Я крипто-бот. Используй /check для анализа рынка.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Доступные команды:\n/start — запуск\n/check — анализ\n/help — помощь")

# Получение исторических цен с CoinGecko
async def fetch_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "2", "interval": "hourly"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            data = response.json()
            return [p[1] for p in data["prices"]]
    except Exception:
        return None

# Простая стратегия
def analyze_moving_average(prices):
    if len(prices) < 50:
        return "недостаточно данных"
    ma20 = np.mean(prices[-20:])
    ma50 = np.mean(prices[-50:])
    if ma20 > ma50:
        return "long"
    elif ma20 < ma50:
        return "short"
    return "none"

# Комплексная проверка
async def check_all_strategies():
    PAIRS = ["bitcoin", "ethereum", "solana", "ripple"]
    SYMBOLS = {
        "bitcoin": "BTC/USDT",
        "ethereum": "ETH/USDT",
        "solana": "SOL/USDT",
        "ripple": "XRP/USDT"
    }

    result_lines = []

    for coin_id in PAIRS:
        symbol = SYMBOLS[coin_id]
        prices = await fetch_price_history(coin_id)

        if not prices:
            result_lines.append(f"❌ Ошибка при получении данных по {symbol}")
            continue

        ma_signal = analyze_moving_average(prices)
        if ma_signal == "long":
            result_lines.append(f"📈 {symbol}: LONG (MA20 > MA50)")
        elif ma_signal == "short":
            result_lines.append(f"📉 {symbol}: SHORT (MA20 < MA50)")
        else:
            result_lines.append(f"⏸️ {symbol}: Нет сигнала (MA20 ≈ MA50)")

    return "\n".join(result_lines)

# Команда /check
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Анализирую рынок...")
    result = await check_all_strategies()
    await update.message.reply_text(result)

# Запуск бота — БЕЗ asyncio.run()
if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))

    print("✅ Бот запущен")
    application.run_polling()  # <--- просто вызываем, без asyncio.run()