from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
import threading
import asyncio

# --- Токен Telegram ---
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# --- Flask ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

# --- Хендлер /start ---
async def start(update, context):
    await update.message.reply_text("Бот работает ✅")

# --- Telegram бот ---
async def run_telegram_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    print("🤖 Бот запускается...")
    await app_bot.run_polling()  # без asyncio.run!

def start_bot_in_thread():
    loop = asyncio.get_event_loop()
    loop.create_task(run_telegram_bot())  # безопасно запускаем бота

# --- Flask запуск ---
def run_flask():
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)

# --- Главный блок ---
if __name__ == "__main__":
    start_bot_in_thread()  # запускаем бота
    run_flask()            # запускаем Flask