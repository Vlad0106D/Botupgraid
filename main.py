from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Dispatcher
import logging
import asyncio
import httpx

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаём приложение telegram-бота
application = ApplicationBuilder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, работаю через webhook и Flask.")

application.add_handler(CommandHandler("start", start))


# Главная страница (чтобы не было 404)
@app.route("/")
async def index():
    return "Бот работает — главная страница"


# Вебхук для телеги
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        update = Update.de_json(await request.get_json(), application.bot)
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
    # Устанавливаем webhook при старте
    asyncio.run(set_webhook())
    # Запускаем Flask с async поддержкой через hypercorn
    import hypercorn.asyncio
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]

    asyncio.run(hypercorn.asyncio.serve(app, config))