from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
import threading
import asyncio

# --- Токен Telegram ---
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# --- Flask ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

# --- Хендлер команды /start ---
async def start(update, context):
    await update.message.reply_text("Бот работает ✅")

# --- Telegram бот ---
async def setup_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    await app_bot.initialize()
    await app_bot.start()
    await app_bot.updater.start_polling()
    await app_bot.updater.idle()

def run_bot():
    asyncio.run(setup_bot())

# --- Flask запуск ---
def run_flask():
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)

# --- Главный блок ---
if __name__ == "__main__":
    # Flask в потоке
    threading.Thread(target=run_flask).start()

    # Бот в основном потоке
    run_bot()