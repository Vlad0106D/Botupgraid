import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask

# Читаем токен из переменных окружения
TOKEN = os.getenv('8000528742:AAHn7SEq5pS3q98VMTBJtCeXwaguMUmrYwE')

app = Flask(__name__)

@app.route('/')
def index():
    return "Flask работает вместе с Telegram-ботом!"

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот.')

def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.run_polling()

if __name__ == '__main__':
    run_bot()