import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import asyncio
import hypercorn.asyncio
from hypercorn.config import Config

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен и URL
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Flask-приложение и Telegram Application
app = Flask(__name__)
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот. Используй /help для справки.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start\n/help")

# Webhook endpoint
@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json()
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return {"ok": True}

# Основная асинхронная функция
async def main():
    # Устанавливаем вебхук
    await app_telegram.bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен")

    # Добавляем хендлеры
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help_command))

    # Настройка и запуск сервера
    config = Config()
    config.bind = ["0.0.0.0:10000"]
    logger.info("Запуск сервера через Hypercorn...")
    await hypercorn.asyncio.serve(app, config)

# Точка входа
if __name__ == "__main__":
    asyncio.run(main())