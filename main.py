import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# === Flask-приложение ===
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Flask-сервер работает параллельно с Telegram-ботом!"

# === Telegram Bot обработчик команды /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Бот и Flask работают одновременно.")

# === Запуск Telegram-бота ===
def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

# === Основной запуск ===
if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Запускаем Flask-сервер (порт обязателен для Render)
    app.run(host='0.0.0.0', port=10000)