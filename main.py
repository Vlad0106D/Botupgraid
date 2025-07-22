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

def run_bot():
    async def main():
        app_bot = ApplicationBuilder().token(TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        await app_bot.run_polling()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

if __name__ == "__main__":
    # Запускаем Telegram-бота в отдельном потоке
    threading.Thread(target=run_bot, daemon=True).start()

    print("🌐 Flask запускается...")
    app.run(host="0.0.0.0", port=10000)