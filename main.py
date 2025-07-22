from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import threading
import asyncio

# Токен твоего бота
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Flask приложение
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Flask и бот работают!"

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает!")

# Асинхронный запуск бота
async def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("🤖 Бот запускается...")
    await application.run_polling()

# Обёртка для запуска в потоке
def run_bot():
    asyncio.run(start_bot())

# Главная точка входа
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot).start()
    # Запускаем Flask сервер
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)