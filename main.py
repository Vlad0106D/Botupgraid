import asyncio
import logging
import httpx
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === Настройки ===
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
CHAT_ID = 776505127

COIN_IDS = ["bitcoin", "ethereum", "solana", "ripple"]
SYMBOLS = {
    "bitcoin": "BTC/USDT",
    "ethereum": "ETH/USDT",
    "solana": "SOL/USDT",
    "ripple": "XRP/USDT"
}

# === Логгирование ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Получение исторических данных с CoinGecko ===
async def fetch_price_history(coin_id, days=7, interval='hourly'):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            prices = [price[1] for price in data["prices"]]
            return prices
    except Exception as e:
        print(f"Ошибка при получении данных {coin_id}: {e}")
        return []

# === Простая стратегия: анализ скользящих средних (MA) ===
def analyze_moving_average(prices):
    if len(prices) < 50:
        return "none"

    ma20 = np.mean(prices[-20:])
    ma50 = np.mean(prices[-50:])

    if ma20 > ma50:
        return "long"
    elif ma20 < ma50:
        return "short"
    else:
        return "none"

# === Командный обработчик /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я трейдинг-бот. Используй команду /check для анализа рынка.")

# === Командный обработчик /check ===
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Анализирую рынок...")

    signals = await check_all_strategies()
    await update.message.reply_text(signals)

# === Анализ всех монет ===
async def check_all_strategies():
    result_lines = []

    for coin_id in COIN_IDS:
        symbol = SYMBOLS.get(coin_id, coin_id.upper())
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

# === Главная функция ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())