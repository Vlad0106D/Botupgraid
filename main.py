import asyncio
import logging
import httpx
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import hypercorn.asyncio
from hypercorn.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"  # поменяй на свой URL!

app = Flask(__name__)
app_telegram = None  # глобальный Application

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это тестовый бот.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команды:\n/start - приветствие\n/help - помощь")

@app.post("/webhook")
async def webhook():
    try:
        data = await request.get_json()  # в Flask >=2.0 async request.get_json()
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return {"ok": True}

async def main():
    global app_telegram
    app_telegram = ApplicationBuilder().token(TOKEN).build()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help_command))

    await app_telegram.initialize()

    # Устанавливаем webhook
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info(f"Webhook установлен: {r.json()}")

    config = Config()
    config.bind = ["0.0.0.0:10000"]

    logger.info("Запуск сервера Flask + Telegram webhook...")
    await hypercorn.asyncio.serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())