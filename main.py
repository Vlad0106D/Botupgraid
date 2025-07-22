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

# --- Хендлер команды /start ---
async def start(update, context):
    await update.message.reply_text("Бот работает ✅")

# --- Telegram бот ---
async def setup_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    print("🤖 Бот запущен")
    await app_bot.run_polling()

# --- Запуск бота в уже работающем event loop ---
def run_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(setup_bot())

# --- Flask запуск ---
def run_flask():
    print("🌐 Flask запускается...")
    run_bot()  # запускаем бота внутри потока Flask
    app.run(host="0.0.0.0", port=10000)

# --- Главный блок ---
if __name__ == "__main__":
    run_flask()