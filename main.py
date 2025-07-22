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

async def setup_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    await app_bot.initialize()
    await app_bot.start()
    await app_bot.run_polling()  # <-- ключевой момент

def run_bot():
    asyncio.run(setup_bot())

def run_flask():
    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()