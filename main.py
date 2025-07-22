import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

import httpx

# 🔐 Твой токен
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# 📦 Flask + Telegram app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🤖 Создание Telegram-приложения
application = ApplicationBuilder().token(TOKEN).build()

# ✅ Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает!")

# 🚀 Регистрируем обработчики
application.add_handler(CommandHandler("start", start))


# 🌐 Flask: корневой маршрут
@app.route("/", methods=["GET"])
def index():
    return "Бот запущен и готов к работе!"


# 🔔 Flask: маршрут вебхука
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        if not application.running:
            await application.initialize()
            await application.start()

        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "OK", 200


# 🌍 Установка вебхука
async def set_webhook():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info(f"Webhook установлен: {r.status_code == 200}")


# 🧠 Запуск бота и Flask
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())

    import hypercorn.asyncio
    import hypercorn.config

    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:10000"]

    loop.run_until_complete(
        hypercorn.asyncio.serve(app, config)
    )