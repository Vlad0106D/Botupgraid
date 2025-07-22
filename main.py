import os
from quart import Quart, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

app = Quart(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я активен.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start\n/help\n/strategy")

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Активных стратегий пока нет.")

# --- Роут для Telegram Webhook ---
@app.post("/webhook")
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return "ok"

# --- Регистрация команд ---
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(CommandHandler("strategy", strategy))

# --- Запуск ---
async def setup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    print("Webhook установлен:", WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))