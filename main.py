import logging
import asyncio
import aiohttp
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Вспомогательные функции для анализа ---

def calc_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi

def sma(values, period):
    if len(values) < period:
        return None
    return np.convolve(values, np.ones(period)/period, mode='valid')

def bollinger_bands(prices, period=20, dev_factor=2):
    if len(prices) < period:
        return None, None, None
    sma_val = sma(prices, period)[-1]
    std_val = np.std(prices[-period:])
    upper = sma_val + dev_factor * std_val
    lower = sma_val - dev_factor * std_val
    return upper, sma_val, lower

def momentum(prices, period=10):
    if len(prices) < period:
        return None
    return prices[-1] - prices[-1 - period]

async def fetch_klines(symbol: str, interval: str = "1h", limit: int = 100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            closes = [float(candle[4]) for candle in data]
            volumes = [float(candle[5]) for candle in data]
            return {"closes": closes, "volumes": volumes}

async def fetch_open_interest(symbol: str, period='1h', limit=30):
    url = f"https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period={period}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if isinstance(data, list) and len(data) > 0:
                oi_values = [float(item['sumOpenInterest']) for item in data]
                return oi_values
            return []

async def analyze_pair(symbol: str):
    klines = await fetch_klines(symbol, interval="1h", limit=100)
    closes = klines["closes"]
    if len(closes) < 50:
        return "NONE", f"Недостаточно данных для анализа {symbol}."

    rsi = calc_rsi(np.array(closes))
    rsi_latest = rsi[-1]

    sma50 = sma(np.array(closes), 50)
    sma200 = sma(np.array(closes), 200)
    sma50_latest = sma50[-1] if sma50 is not None and len(sma50) > 0 else None
    sma200_latest = sma200[-1] if sma200 is not None and len(sma200) > 0 else None

    mom = momentum(np.array(closes), 10)
    upper_bb, mid_bb, lower_bb = bollinger_bands(np.array(closes), 20, 2)

    oi = await fetch_open_interest(symbol, '1h', 30)
    oi_trend = None
    if len(oi) >= 2:
        oi_trend = "растёт" if oi[-1] > oi[-2] else "падает"

    price_latest = closes[-1]

    conditions_long = [
        rsi_latest < 30 if rsi_latest else False,
        sma50_latest and sma200_latest and price_latest > sma50_latest > sma200_latest,
        mom and mom > 0,
        price_latest < mid_bb if mid_bb else False,
        oi_trend == "растёт",
    ]

    conditions_short = [
        rsi_latest > 70 if rsi_latest else False,
        sma50_latest and sma200_latest and price_latest < sma50_latest < sma200_latest,
        mom and mom < 0,
        price_latest > mid_bb if mid_bb else False,
        oi_trend == "падает",
    ]

    explanation = (
        f"RSI: {rsi_latest:.2f}\n"
        f"SMA50: {sma50_latest:.2f if sma50_latest else 'n/a'}\n"
        f"SMA200: {sma200_latest:.2f if sma200_latest else 'n/a'}\n"
        f"Momentum (10): {mom:.2f if mom else 'n/a'}\n"
        f"Цена: {price_latest:.2f}\n"
        f"Open Interest: {oi[-1] if oi else 'n/a'} ({oi_trend})\n"
        f"Полосы Боллинджера: нижняя {lower_bb:.2f if lower_bb else 'n/a'}, средняя {mid_bb:.2f if mid_bb else 'n/a'}, верхняя {upper_bb:.2f if upper_bb else 'n/a'}"
    )

    if all(conditions_long):
        return "LONG", f"Сигнал LONG по {symbol}.\n" + explanation
    elif all(conditions_short):
        return "SHORT", f"Сигнал SHORT по {symbol}.\n" + explanation
    else:
        return "NONE", f"Сигнал отсутствует по {symbol}.\n" + explanation

# --- Команда /check для Telegram ---

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начинаю анализ... Это может занять несколько секунд.")
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
    tasks = [analyze_pair(symbol) for symbol in pairs]
    results = await asyncio.gather(*tasks)

    messages = []
    for symbol, (signal, explanation) in zip(pairs, results):
        messages.append(f"{symbol}: {signal}\n{explanation}\n")

    await update.message.reply_text("\n\n".join(messages))

# --- Команды старт и хелп ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я торговый бот.\n"
        "Используй команду /check для комплексного анализа криптопар."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Приветствие\n"
        "/help - Помощь\n"
        "/check - Запуск анализа всех стратегий"
    )

# --- Главная функция запуска бота ---

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())