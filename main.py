import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает!")

# /check — заглушка (вставим аналитику позже)
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализ рынка... (пока заглушка)")

# Основная асинхронная функция
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    print("Бот запущен ✅")
    await app.run_polling()

# Запуск
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())