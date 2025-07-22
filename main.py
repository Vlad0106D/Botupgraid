import logging
import asyncio
import os

from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import httpx

# === ТВОЙ ТОКЕН ===
BOT_TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask app ===
flask_app = Flask(__name__)

# === Telegram Application ===
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает через Webhook!")

app_telegram.add_handler(CommandHandler("start", start))

# === Асинхронный event loop (совместимый с Render) ===
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# === Webhook endpoint ===
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), app_telegram.bot)
        logger.info("Получен update: %s", update)
        future = asyncio.run_coroutine_threadsafe(app_telegram.process_update(update), loop)
        future.result(timeout=10)
    except Exception as e:
        logger.error("Ошибка при обработке update: %s", e)
    return "ok", 200

# === Страница по / (для Render UI) ===
@flask_app.route("/", methods=["GET"])
def index():
    return "✅ Telegram бот работает через Webhook!", 200

# === Установка webhook перед запуском Flask ===
async def set_webhook():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info("Webhook установлен: %s", resp.status_code == 200)

if __name__ == "__main__":
    loop.run_until_complete(set_webhook())
    logger.info("Запуск Flask-сервера...")
    flask_app.run(host="0.0.0.0", port=10000)