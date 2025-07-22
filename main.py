import logging
import asyncio
from quart import Quart, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)
application = ApplicationBuilder().token(TOKEN).build()

enabled_strategies = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой трейдинг-бот.")

@app.post("/webhook")
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, application.bot)
    try:
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
        return "error", 500
    return "ok"

if __name__ == "__main__":
    async def main():
        # ВНИМАНИЕ: сначала инициализируем приложение
        await application.initialize()

        webhook_url = "https://botupgraid.onrender.com/webhook"
        await application.bot.set_webhook(webhook_url)
        logger.info("Webhook установлен")

        # Добавляем хендлеры после инициализации
        application.add_handler(CommandHandler("start", start))

        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        config = Config()
        config.bind = ["0.0.0.0:10000"]
        await serve(app, config)

    asyncio.run(main())