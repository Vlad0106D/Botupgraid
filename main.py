from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот запущен и работает.")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — запуск\n"
        "/help — помощь\n"
        "/strategy — активные стратегии"
    )

# /strategy
async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_strategies = [
        "1. 📊 Комплексный технический анализ (RSI, MA, Momentum, Bollinger, OI, Capital Flow)"
    ]
    await update.message.reply_text("Активные стратегии:\n" + "\n".join(active_strategies))

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("strategy", strategy_command))

# Запуск
print("Бот запущен...")
app.run_polling()