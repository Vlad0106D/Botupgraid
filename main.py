from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import threading
import asyncio

from strategies import generate_signals

# 🔐 ТВОЙ ТОКЕН
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Flask-приложение
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот и веб-интерфейс работают ✅"

# Команды Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен ✅")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signals, explanation, timestamp = generate_signals()
    msg = f"📊 Сигналы на {timestamp}:\n\n"
    for pair, action in signals.items():
        reason = explanation.get(pair, "")
        msg += f"{pair}: {action} — {reason}\n"
    await update.message.reply_text(msg)

# Асинхронная функция запуска бота
async def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", signal))
    await application.run_polling()

# Поток, в котором мы создаём loop и запускаем бота
def run_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

# Flask запуск в отдельном потоке
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Главный запуск
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_bot_thread).start()