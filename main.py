import logging
import httpx
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import nest_asyncio

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()  # для Render

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]

# Получение исторических данных с Binance
async def fetch_klines(symbol: str, interval: str = "1h", limit: int = 100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return [float(candle[4]) for candle in data]  # закрытия
        except Exception as e:
            logging.error(f"Ошибка при получении данных {symbol}: {e}")
            return None

# Расчёт RSI
def calculate_rsi(prices, period: int = 14):
    if len(prices) < period + 1:
        return None
    deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
    gains = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]
    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Используй /check для анализа рынка.")

# Команда /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start – запустить бота\n/check – получить сигналы\n/strategy – активные стратегии")

# Команда /strategy
async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Активная стратегия: Комплексный технический анализ (RSI)")

# Команда /check — основной анализ
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализирую рынок...")
    results = []
    for symbol in symbols:
        prices = await fetch_klines(symbol)
        if prices is None:
            results.append(f"{symbol}: ошибка получения данных.")
            continue
        rsi = calculate_rsi(prices)
        if rsi is None:
            results.append(f"{symbol}: недостаточно данных для RSI.")
            continue

        if rsi < 30:
            signal = "🔵 LONG (перепродан)"
        elif rsi > 70:
            signal = "🔴 SHORT (перекуплен)"
        else:
            signal = "⚪️ Нейтрально"

        results.append(f"{symbol}: RSI = {rsi:.2f} → {signal}")

    await update.message.reply_text("\n".join(results))

# Запуск приложения
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("strategy", strategy))
    app.add_handler(CommandHandler("check", check))
    await app.initialize()
    await app.start()
    print("Бот запущен...")
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())