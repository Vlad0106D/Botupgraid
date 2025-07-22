from telegram import Update
from telegram.ext import ContextTypes

# Обработчик команды /signal
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Это тестовый сигнал. Всё работает!")
