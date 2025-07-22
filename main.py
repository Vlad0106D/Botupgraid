import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 ТВОЙ ТОКЕН
BOT_TOKEN = "6452431495:AAHDbGpA-TeEB7e2q9iZ7JZ_zkFGLkP7fco"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# 🔧 ЛОГИ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 🌐 Flask-приложение
app = Flask(__name__)
app_telegram = None  # Переменная под Application

# 🔁 /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("✅ Получен /start")
    await update.message.reply_text("👋 Привет! Бот работает через Webhook!")

# 📩 Обработка входящих обновлений от Telegram
@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), app_telegram.bot)
        await app_telegram.process_update(update)
        return "ok"
    return "not allowed", 405

# 🏁 Ручная проверка / запуска сервиса
@app.route("/", methods=["GET"])
def home():
    return "✅ Сервис Telegram-бота работает!"

# 🚀 Старт приложения
if __name__ == "__main__":
    import asyncio
    from telegram.ext import Application

    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем команды
    app_telegram.add_handler(CommandHandler("start", start))

    # Устанавливаем Webhook (однократно при запуске)
    async def set_webhook():
        success = await app_telegram.bot.set_webhook(WEBHOOK_URL)
        if success:
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        else:
            logging.error("❌ Webhook не удалось установить")

    # Запускаем установку Webhook
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())

    # Запуск Flask на порту 10000
    app.run(host="0.0.0.0", port=10000)