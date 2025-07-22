from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio

# === Токен бота ===
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# === Flask ===
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

# === Telegram-команда /start ===
async def start(update, context):
    await update.message.reply_text("Бот работает ✅")

# === Главная асинхронная функция ===
async def main():
    # Telegram bot
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))

    # Запуск Telegram бота параллельно с Flask
    runner = asyncio.create_task(app_bot.run_polling())

    # Flask — через встроенный async-сервер
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    config = Config()
    config.bind = ["0.0.0.0:10000"]

    flask_server = serve(app, config)

    # Ожидание завершения обоих
    await asyncio.gather(runner, flask_server)

if __name__ == "__main__":
    asyncio.run(main())