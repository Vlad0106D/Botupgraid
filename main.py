import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

app = Flask(__name__)

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот. Используй /help для справки.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start\n/help")

# Инициализация Application Telegram
app_telegram = ApplicationBuilder().token(TOKEN).build()

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("help", help_command))

# Установка webhook при запуске
@app.before_first_request
def set_webhook():
    url = "https://botupgraid.onrender.com/webhook"
    result = app_telegram.bot.set_webhook(url)
    logger.info(f"Webhook установлен: {result}")

# Обработка входящих обновлений
@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json()  # ВАЖНО: без await
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return {"ok": True}

# Запуск Flask через Hypercorn
if __name__ == "__main__":
    import hypercorn.asyncio
    import asyncio

    config = hypercorn.Config()
    config.bind = ["0.0.0.0:10000"]
    logger.info("Запуск Flask-сервера...")
    asyncio.run(hypercorn.asyncio.serve(app, config))