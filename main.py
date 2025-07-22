import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# 🔐 Твой токен бота
TOKEN = "6171611576:AAHd6Cv3PqWldIMXeTx--Se8DRQWwJjnbOc"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

app = Flask(__name__)

# Создание приложения Telegram
application = ApplicationBuilder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает по вебхукам ✅")

# Добавление хэндлеров
application.add_handler(CommandHandler("start", start))

# Роут для установки вебхука
@app.route("/set_webhook")
def set_webhook():
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    return "Webhook установлен ✅"

# Роут вебхука, на который Telegram будет слать апдейты
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

# Проверка работы сайта
@app.route("/")
def index():
    return "Бот работает ✅"

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run(host="0.0.0.0", port=10000)