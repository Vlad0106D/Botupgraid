import os
import logging
import asyncio
from quart import Quart, jsonify
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

from strategy import check_all_strategies

# Telegram Bot Token
TOKEN = os.environ.get("BOT_TOKEN") or "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
TELEGRAM_CHAT_ID = 776505127

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quart App (для веб-интерфейса)
app = Quart(__name__)
telegram_app = None  # Будет создан позже


@app.route("/")
async def index():
    return jsonify({"status": "бот работает"})


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот запущен и готов к работе!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Команды:\n/start — запуск\n/help — помощь\n/check — анализ рынка")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализирую рынок...")
    result = await check_all_strategies()
    await update.message.reply_text(result)


async def run_bot():
    global telegram_app
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(CommandHandler("check", check_command))

    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    app.run(loop=loop, host="0.0.0.0", port=10000)