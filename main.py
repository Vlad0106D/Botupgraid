from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# --- Telegram TOKEN ---
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# --- Flask app ---
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Бот и Flask работают"

# --- Хендлер команды /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Бот работает!")

# --- Асинхронный запуск Telegram-бота ---
async def main():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    await app_bot.initialize()
    await app_bot.start()
    await app_bot.updater.start_polling()
    print("🤖 Бот запущен")
    # НЕ await idle() — Render упадёт!
    while True:
        await asyncio.sleep(60)

# --- Запуск Flask и бота ---
if __name__ == "__main__":
    import threading

    # Flask в потоке
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()

    # Запуск асинхронного Telegram-бота
    asyncio.run(main())