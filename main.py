import os
import logging
from quart import Quart, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Логирование
logging.basicConfig(level=logging.INFO)

# Quart app
app = Quart(__name__)
telegram_app = None  # сюда позже передадим приложение Telegram


@app.before_serving
async def before_serving():
    global telegram_app
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    # Команды
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(CommandHandler("strategy", strategy))

    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook set.")
    await telegram_app.start()


@app.route("/", methods=["GET"])
async def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"


@app.after_serving
async def after_serving():
    await telegram_app.stop()
    await telegram_app.shutdown()


# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Используй /help для списка команд.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start — запуск\n/strategy — активные стратегии")


async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нет активных стратегий.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)