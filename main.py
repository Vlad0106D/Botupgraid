import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === ТВОЙ ТОКЕН ===
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://botupgraid.onrender.com{WEBHOOK_PATH}"

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask приложение ===
flask_app = Flask(__name__)

# === Новый event loop для телеграма ===
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# === Создание Telegram Application ===
app_telegram = Application.builder().token(TOKEN).build()

# === Обработка команды /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает через Webhook!")

app_telegram.add_handler(CommandHandler("start", start))

# === Webhook endpoint ===
@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app_telegram.bot)
    asyncio.run_coroutine_threadsafe(app_telegram.process_update(update), loop)
    return "OK", 200

# === Установка webhook и запуск Flask ===
async def main():
    await app_telegram.initialize()
    await app_telegram.bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен")
    await app_telegram.start()

if __name__ == "__main__":
    loop.run_until_complete(main())
    flask_app.run(host="0.0.0.0", port=10000)