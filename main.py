import asyncio
import aiohttp
from quart import Quart
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
TELEGRAM_CHAT_ID = 776505127

# Активные стратегии
active_strategies = {
    "Комплексный технический анализ": True
}

app = Quart(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Используй /help для справки.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — запуск бота\n"
        "/help — справка\n"
        "/strategy — активные стратегии\n"
        "/check — выполнить анализ"
    )


async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if active_strategies:
        message = "Активные стратегии:\n" + "\n".join(f"- {name}" for name in active_strategies if active_strategies[name])
    else:
        message = "Нет активных стратегий."
    await update.message.reply_text(message)


# Простейший пример сигнала (заглушка)
async def analyze_market():
    signals = []

    # Пример анализа для BTC/USDT на основе фейковых публичных данных
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT") as resp:
            if resp.status == 200:
                data = await resp.json()
                price = float(data["price"])
                if price < 50000:
                    signals.append("🟢 BTC/USDT сигнал: LONG (Цена ниже 50,000)")
                else:
                    signals.append("🔴 BTC/USDT сигнал: SHORT (Цена выше 50,000)")
            else:
                signals.append("Ошибка при получении данных BTC/USDT")

    return signals


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not active_strategies:
        await update.message.reply_text("Нет активных стратегий.")
        return

    await update.message.reply_text("Анализирую рынок...")

    try:
        signals = await analyze_market()
        if signals:
            for s in signals:
                await update.message.reply_text(s)
        else:
            await update.message.reply_text("Нет сигналов на данный момент.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при анализе: {str(e)}")


# Telegram bot setup
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("strategy", strategy))
telegram_app.add_handler(CommandHandler("check", check_command))


# Запуск Telegram и Quart параллельно
async def run():
    print("Бот запущен...")
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    await telegram_app.updater.wait()

@app.before_serving
async def startup():
    asyncio.create_task(run())

@app.route("/")
async def index():
    return "Трейдинг-бот работает."


if __name__ == "__main__":
    import hypercorn.asyncio
    import hypercorn.config

    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:8000"]
    asyncio.run(hypercorn.asyncio.serve(app, config))