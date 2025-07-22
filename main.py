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

async def fetch_prices(coin_id: str, days: int = 15):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        print(f"Ответ для {coin_id}: ключи {list(data.keys())}")
        prices = data.get("prices")
        if not prices:
            raise ValueError("Пустой список цен 'prices'")
        return [p[1] for p in prices]

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
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
    await update.message.reply_text("Начинаю анализ...")

    results = []
    for symbol, coin_id in COINS.items():
        try:
            prices = await fetch_prices(coin_id)
            rsi = calculate_rsi(prices)
            current_price = prices[-1]
            results.append(
                f"{symbol}/USDT\nЦена: ${current_price:.2f}\nRSI(14): {rsi if rsi is not None else 'Недостаточно данных'}\n"
            )
        except Exception as e:
            print(f"Ошибка при получении данных по {symbol}/USDT: {e}")
            results.append(f"❌ Ошибка при получении данных по {symbol}/USDT: {e}")

    await update.message.reply_text("\n".join(results))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Используй /check для технического анализа."
    )

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", check_command))

    print("Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())