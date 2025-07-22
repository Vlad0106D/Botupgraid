import logging
import httpx
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

ACTIVE_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]


async def fetch_klines(symbol: str, interval: str = "1h", limit: int = 100):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()


def calculate_rsi(prices: list, period: int = 14):
    if len(prices) < period + 1:
        return None
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


async def analyze_pair(symbol: str):
    try:
        klines = await fetch_klines(symbol)
        closes = [float(candle[4]) for candle in klines]
        rsi = calculate_rsi(closes)

        if rsi is None:
            return f"{symbol}: Недостаточно данных для RSI."

        if rsi > 70:
            signal = "🔻 Short"
        elif rsi < 30:
            signal = "🚀 Long"
        else:
            signal = "❌ No Signal"

        return f"{symbol} — RSI: {rsi:.2f} — {signal}"

    except Exception as e:
        return f"Ошибка при анализе {symbol}: {e}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Используйте /check для анализа рынка.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команды:\n/start — запуск\n/help — помощь\n/check — анализ рынка")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализирую рынок...")

    results = await asyncio.gather(*[analyze_pair(pair) for pair in ACTIVE_PAIRS])
    await update.message.reply_text("\n".join(results))


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check))

    print("Бот запущен...")
    app.run_polling()