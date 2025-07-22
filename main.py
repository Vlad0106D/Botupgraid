from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import threading
import asyncio

from strategies import generate_signals

# 🔐 ТВОЙ ТОКЕН
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

app = Flask(__name__)

@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен ✅")

# Команда /signal
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signals, explanation, timestamp = generate_signals()
    msg = f"📊 Сигналы на {timestamp}:\n\n"
    for pair, action in signals.items():
        reason = explanation.get(pair, "")
        msg += f"{pair}: {action} — {reason}\n"
    await update.message.reply_text(msg)

# Асинхронный запуск бота
async def setup_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", signal))
    await application.run_polling()

# Запуск Flask в отдельном потоке
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Основной запуск
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    loop = asyncio.get_event_loop()
    loop.create_task(setup_bot())
    loop.run_forever()