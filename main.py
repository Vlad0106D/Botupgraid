from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from strategies import generate_signals
import asyncio

# --- Токен Telegram ---
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# --- Flask ---
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Бот и веб-интерфейс работают"

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот запущен и работает!")

# --- Команда /signal ---
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signals, explanation, timestamp = generate_signals()
    text = f"📊 Сигналы на {timestamp}:\n\n"
    for pair, sig in signals.items():
        reason = explanation.get(pair, "")
        text += f"• {pair}: {sig} — {reason}\n"
    await update.message.reply_text(text)

# --- Главный запуск ---
async def main():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("signal", signal))

    # Запуск Flask в фоне
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(app.run, host="0.0.0.0", port=10000))

    # Запуск Telegram-бота
    await app_bot.run_polling()

# --- Запуск ---
if __name__ == "__main__":
    asyncio.run(main())