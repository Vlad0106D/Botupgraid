import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import httpx
import numpy as np
from datetime import datetime, timedelta

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
PAIRS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple"
}

async def fetch_ohlcv(coin_id: str, days: int = 2) -> list:
    """Получить OHLCV данные с CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=hourly"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        prices = data["prices"][-100:]  # последние 100 часовых свечей
        return prices

def calculate_rsi(prices: list, period: int = 14) -> float:
    prices = np.array(prices)
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def calculate_ma(prices: list, period: int) -> float:
    return round(np.mean(prices[-period:]), 2)

def analyze(prices: list) -> dict:
    close_prices = [p[1] for p in prices]  # цены закрытия
    rsi = calculate_rsi(close_prices)
    ma50 = calculate_ma(close_prices, 50)
    ma200 = calculate_ma(close_prices, 100)  # используем 100 точек, эквивалент ~4 дня
    last_price = close_prices[-1]

    signal = "none"
    reasons = []

    if rsi < 30:
        signal = "long"
        reasons.append("RSI ниже 30 (перепроданность)")
    elif rsi > 70:
        signal = "short"
        reasons.append("RSI выше 70 (перекупленность)")

    if last_price > ma50 > ma200:
        signal = "long"
        reasons.append("Цена выше MA50 и MA200")
    elif last_price < ma50 < ma200:
        signal = "short"
        reasons.append("Цена ниже MA50 и MA200")

    return {
        "price": round(last_price, 2),
        "rsi": rsi,
        "ma50": ma50,
        "ma200": ma200,
        "signal": signal,
        "reasons": reasons
    }

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализирую рынок...")

    results = []
    for pair, coin_id in PAIRS.items():
        try:
            prices = await fetch_ohlcv(coin_id)
            analysis = analyze(prices)
            signal = analysis["signal"].upper()
            reasons = "\n- " + "\n- ".join(analysis["reasons"]) if analysis["reasons"] else "Нет явных сигналов"
            result = f"🔹 {pair}\n" \
                     f"Текущая цена: {analysis['price']}$\n" \
                     f"RSI: {analysis['rsi']}\n" \
                     f"MA50: {analysis['ma50']}\n" \
                     f"MA200: {analysis['ma200']}\n" \
                     f"📊 Сигнал: *{signal}*\nПричины:{reasons}"
            results.append(result)
        except Exception as e:
            results.append(f"❌ Ошибка при анализе {pair}: {e}")

    await update.message.reply_text("\n\n".join(results), parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я трейдинг-бот. Используй команду /check для анализа рынка.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())