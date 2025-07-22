from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот запущен и работает.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — запуск\n"
        "/help — помощь\n"
        "/strategy — активные стратегии"
    )

# Команда /strategy
async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_strategies = [
        "1. 📊 Комплексный технический анализ (RSI, MA, Momentum, Bollinger, OI, Capital Flow)"
    ]
    text = "Активные стратегии:\n" + "\n".join(active_strategies)
    await update.message.reply_text(text)

# Создаем и запускаем приложение
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("strategy", strategy_command))

print("Бот запущен...")
app.run_polling()