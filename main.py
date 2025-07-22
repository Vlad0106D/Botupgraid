import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
import httpx

# Telegram Bot Token
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app_flask = Flask(__name__)

# Telegram Application
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает через Webhook!")

# Регистрируем обработчик
app_telegram.add_handler(CommandHandler("start", start))

# Устанавливаем webhook
async def set_webhook():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info("Webhook установлен: %s", response.json().get("ok", False))

# Запускаем вебхук
@app_flask.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.exception("Ошибка при обработке update:")
    return "OK"

# Запуск сервера и webhook
if __name__ == "__main__":
    asyncio.run(set_webhook())
    logger.info("Запуск Flask-сервера...")
    app_flask.run(host="0.0.0.0", port=10000)