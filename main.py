import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://botupgraid.onrender.com" + WEBHOOK_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
loop = asyncio.get_event_loop()

app_telegram = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает через Webhook!")

app_telegram.add_handler(CommandHandler("start", start))

@flask_app.route("/")
def index():
    return "🤖 Бот работает через Webhook!"

@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"Получен update: {data}")
    update = Update.de_json(data, app_telegram.bot)
    future = asyncio.run_coroutine_threadsafe(app_telegram.process_update(update), loop)
    try:
        future.result(timeout=10)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "OK", 200

async def set_webhook():
    await app_telegram.bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен")

if __name__ == "__main__":
    loop.run_until_complete(app_telegram.initialize())
    loop.run_until_complete(set_webhook())
    flask_app.run(host="0.0.0.0", port=10000)