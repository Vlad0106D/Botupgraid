import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# 🔐 Твой токен
TOKEN = "6499005496:AAELkXqJe63d3hu-sq4PtMv4vTt3eD7j2So"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Инициализация Flask и бота
app = Flask(__name__)
bot = Bot(token=TOKEN)

# --- Хэндлеры бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает через вебхук!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

# --- Flask webhook endpoint ---
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# --- Установка вебхука ---
@app.route('/set_webhook')
def set_webhook():
    success = bot.set_webhook(WEBHOOK_URL)
    return f"Webhook установлен: {success}"

# --- Telegram application ---
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Flask запуск ---
if __name__ == '__main__':
    print("🔗 Сервис запущен, открой /set_webhook один раз после деплоя")
    app.run(host='0.0.0.0', port=10000)