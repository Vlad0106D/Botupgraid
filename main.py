from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)
import asyncio
import logging
import os

# === Конфигурация ===
BOT_TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://botupgraid.onrender.com{WEBHOOK_PATH}"

# === Логгирование ===
logging.basicConfig(level=logging.INFO)

# === Flask приложение ===
flask_app = Flask(__name__)

# === Telegram bot application ===
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

# === Хэндлеры ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает через Webhook!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Вы сказали: {update.message.text}")

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Flask маршрут для Webhook ===
@flask_app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), app_telegram.bot)
        await app_telegram.process_update(update)
        return "OK", 200

# === Проверка сервера (страница по умолчанию) ===
@flask_app.route("/", methods=["GET"])
def index():
    return "🤖 Бот запущен и слушает Webhook!"

# === Установка Webhook ===
async def set_webhook():
    webhook_set = await app_telegram.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"Webhook установлен: {webhook_set}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))