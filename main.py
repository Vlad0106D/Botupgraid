import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"  # ← твой бот токен

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я работаю.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Доступные команды:\n/start — запуск\n/help — помощь")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("✅ Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())