import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Токен вашего бота
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я трейдинг-бот.\n"
        "Используй /help для списка команд."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Запуск бота\n"
        "/help - Помощь\n"
        "/check - Проверить активные стратегии"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Пример простой стратегии — можешь заменить на свою логику
    strategy_signal = {
        "pair": "BTC/USDT",
        "signal": "Long",
        "reason": "RSI ниже 30, возможен разворот вверх"
    }
    response = (
        f"Активные стратегии:\n"
        f"Пара: {strategy_signal['pair']}\n"
        f"Сигнал: {strategy_signal['signal']}\n"
        f"Обоснование: {strategy_signal['reason']}"
    )
    await update.message.reply_text(response)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())