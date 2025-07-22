from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
import asyncio

# 🔐 Твой токен
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask-приложение
app = Flask(__name__)

# Telegram Bot Application
application = ApplicationBuilder().token(TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает (Webhook)")

# /signal (пока без логики стратегии)
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Здесь будет сигнал (тестовая заглушка)")

# Регистрируем команды
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signal", signal))

# Главная страница
@app.route("/")
def home():
    return "✅ Бот и Flask работают. Webhook активен?"

# Установка Webhook вручную через URL
@app.route("/set_webhook")
def set_webhook():
    success = asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    return f"Webhook установлен: {success}"

# Приём запросов от Telegram
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        app.logger.info("📨 Update received: %s", data)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        app.logger.error("❌ Ошибка в webhook: %s", e)
        return "error", 500
    return "ok"

# Запуск Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)