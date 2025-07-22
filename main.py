import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import httpx
import numpy as np

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
}

# Получение исторических цен для расчёта RSI (14 периодов)
async def fetch_prices(coin_id: str, days: int = 15):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        prices = [p[1] for p in data["prices"]]
        return prices

# Простая функция расчёта RSI
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None  # недостаточно данных
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начинаю анализ по парам...")

    results = []
    for symbol, coin_id in COINS.items():
        try:
            prices = await fetch_prices(coin_id)
            rsi = calculate_rsi(prices)
            current_price = prices[-1]
            results.append(f"{symbol}/USDT\nЦена: ${current_price:.2f}\nRSI(14): {rsi if rsi is not None else 'Недостаточно данных'}\n")
        except Exception as e:
            results.append(f"❌ Ошибка при получении данных по {symbol}/USDT: {e}")

    answer = "\n".join(results)
    await update.message.reply_text(answer)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для технического анализа. Используй команду /check для анализа.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", check_command))

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())