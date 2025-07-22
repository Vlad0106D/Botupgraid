from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, render_template
import threading

# Твой токен бота
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Создание Flask-приложения
app = Flask(__name__)

# Маршрут по умолчанию
@app.route('/')
def index():
    return "✅ Flask и бот работают!"

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, всё работает ✅")

# Функция запуска Telegram-бота
def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("🤖 Бот запускается...")
    application.run_polling()

# Точка входа
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot).start()
    # Запускаем Flask
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)