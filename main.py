import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import asyncio

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://botupgraid.onrender.com{WEBHOOK_PATH}"
PORT = 10000

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Создаём Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Telegram бот.")

application.add_handler(CommandHandler("start", start))


@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        json_update = request.get_json()  # НЕ await!
        update = Update.de_json(json_update, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "ok"


@app.route("/")
def index():
    return "Telegram bot is running."


async def set_webhook():
    ok = await application.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {ok}")


if __name__ == "__main__":
    # Запускаем в asyncio цикле установку webhook и Flask через Hypercorn
    async def main():
        await set_webhook()
        # Запускаем Flask async-сервер через Hypercorn
        from hypercorn.asyncio import serve
        from hypercorn.config import Config

        config = Config()
        config.bind = [f"0.0.0.0:{PORT}"]
        await serve(app, config)

    asyncio.run(main())