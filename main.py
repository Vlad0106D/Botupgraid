from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
import threading
import asyncio

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

app = Flask(__name__)

@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

async def start(update, context):
    await update.message.reply_text("Бот работает ✅")

def run_flask():
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)

async def run_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    await app_bot.run_polling()

if __name__ == "__main__":
    # Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()

    # Бот в основном потоке (asyncio.run можно вызвать только из главного потока)
    asyncio.run(run_bot())