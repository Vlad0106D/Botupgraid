from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
import threading
import asyncio

# --- Telegram Bot Setup ---
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

app = Flask(__name__)

# Команда /start
async def start(update, context):
    await update.message.reply_text("Бот работает ✅")

# Функция запуска Telegram-бота
async def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.run_polling()

# Функция запуска Flask в отдельном потоке
def run_flask():
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)

# Корневая страница
@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

# --- Главный блок запуска ---
if __name__ == "__main__":
    # Запускаем Flask в фоне
    threading.Thread(target=run_flask).start()

    # Запускаем Telegram-бот в основном потоке
    asyncio.run(start_bot())