import asyncio
import logging

from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import httpx
from hypercorn.asyncio import serve
from hypercorn.config import Config

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Создаём приложение телеграм-бота
application = ApplicationBuilder().token(TOKEN).build()


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, работаю через webhook и Flask.")

application.add_handler(CommandHandler("start", start))


@app.route("/")
async def index():
    return "Бот работает — главная страница"


@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        json_update = await request.get_json()
        update = Update.de_json(json_update, application.bot)
        # Обработка update через Application
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "ok"


async def set_webhook():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        if response.status_code == 200:
            logger.info(f"Webhook установлен: {response.json().get('ok')}")
        else:
            logger.error(f"Ошибка установки webhook: {response.text}")


if __name__ == "__main__":
    # При старте сначала инициализируем приложение и ставим webhook
    asyncio.run(application.initialize())
    asyncio.run(set_webhook())

    config = Config()
    config.bind = ["0.0.0.0:10000"]

    # Запускаем hypercorn (async сервер) с нашим Flask-приложением
    asyncio.run(serve(app, config))