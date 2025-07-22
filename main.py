import asyncio
from quart import Quart, jsonify, render_template_string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import httpx
import numpy as np

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

app = Quart(__name__)

# Криптопары для анализа
COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP"
}

# ----------- Технический анализ -----------

def simple_moving_average(prices, period=14):
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])

def rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def bollinger_bands(prices, period=20, k=2):
    if len(prices) < period:
        return None, None, None
    sma = simple_moving_average(prices, period)
    std = np.std(prices[-period:])
    upper = sma + k * std
    lower = sma - k * std
    return lower, sma, upper

def momentum(prices, period=10):
    if len(prices) < period + 1:
        return None
    return prices[-1] - prices[-1 - period]

# ----------- Получение данных с CoinGecko -----------

async def get_price_history(coin_id: str, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # prices - список [ [timestamp, price], ... ]
        prices = [price[1] for price in data["prices"]]
        return prices

# ----------- Анализ и сигналы -----------

async def analyze_coin(coin_id):
    prices = await get_price_history(coin_id, 30)
    if not prices or len(prices) < 20:
        return "Недостаточно данных для анализа."

    rsi_val = rsi(prices)
    sma_20 = simple_moving_average(prices, 20)
    lower_bb, mid_bb, upper_bb = bollinger_bands(prices)
    mom = momentum(prices)

    latest_price = prices[-1]

    # Простая логика сигналов
    signals = []
    if rsi_val is not None:
        if rsi_val < 30:
            signals.append("RSI показывает перепроданность — потенциальный сигнал на покупку")
        elif rsi_val > 70:
            signals.append("RSI показывает перекупленность — потенциальный сигнал на продажу")
        else:
            signals.append(f"RSI нейтрален: {rsi_val:.1f}")

    if mom is not None:
        if mom > 0:
            signals.append("Momentum положительный — тренд вверх")
        else:
            signals.append("Momentum отрицательный — тренд вниз")

    if latest_price < lower_bb:
        signals.append("Цена ниже нижней полосы Боллинджера — потенциальная перепроданность")
    elif latest_price > upper_bb:
        signals.append("Цена выше верхней полосы Боллинджера — потенциальная перекупленность")
    else:
        signals.append("Цена в пределах полос Боллинджера")

    return "\n".join(signals)

async def analyze_all():
    results = {}
    for coin_id, symbol in COINS.items():
        try:
            analysis = await analyze_coin(coin_id)
        except Exception as e:
            analysis = f"Ошибка анализа: {e}"
        results[symbol] = analysis
    return results

# ----------- Telegram боты -----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь /check, чтобы получить сигналы по BTC, ETH, SOL, XRP.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Идет анализ, подождите секунду...")
    results = await analyze_all()
    msg = ""
    for symbol, text in results.items():
        msg += f"*{symbol}*\n{text}\n\n"
    await update.message.reply_markdown(msg.strip())

# ----------- Запуск Telegram приложения -----------

telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("check", check))

# ----------- Веб-сервер на Quart -----------

@app.route("/")
async def index():
    results = await analyze_all()
    html = """
    <h1>Крипто-сигналы (BTC, ETH, SOL, XRP)</h1>
    {% for symbol, analysis in results.items() %}
    <h2>{{ symbol }}</h2>
    <pre>{{ analysis }}</pre>
    {% endfor %}
    """
    return await render_template_string(html, results=results)

# ----------- Главная точка входа -----------

async def main():
    # Удаляем вебхук, чтобы не было конфликта с polling
    await telegram_app.bot.delete_webhook(drop_pending_updates=True)

    # Запускаем Telegram polling и Quart сервер параллельно
    # Запускаем в отдельных задачах
    polling_task = asyncio.create_task(telegram_app.run_polling())

    # Quart запускается через Hypercorn (асинхронный сервер) ниже в __main__

    await polling_task  # Ждем polling (он не завершится пока бот работает)

if __name__ == "__main__":
    import hypercorn.asyncio
    import hypercorn.config

    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:5000"]

    loop = asyncio.get_event_loop()

    # Запускаем одновременно Quart и Telegram polling
    # Quart сервер запускается через hypercorn.asyncio.serve
    # Telegram polling - как задача

    async def run_all():
        polling_task = asyncio.create_task(telegram_app.run_polling())
        quart_task = asyncio.create_task(hypercorn.asyncio.serve(app, config))
        await asyncio.gather(polling_task, quart_task)

    loop.run_until_complete(run_all())