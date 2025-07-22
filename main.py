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

# Асинхронный запуск Telegram Application
app_telegram = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает через Webhook!")

# Добавляем хендлер
app_telegram.add_handler(CommandHandler("start", start))

@flask_app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "OK", 200

async def setup():
    await app_telegram.initialize()
    await app_telegram.bot.set_webhook(WEBHOOK_URL)
    await app_telegram.start()
    logger.info("✅ Webhook установлен и бот запущен")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(setup())
    flask_app.run(host="0.0.0.0", port=10000)