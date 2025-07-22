import logging
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "6437536295:AAG9dcbMBmnDb6s0cQZCUJsIaT1skJfPO8s"
APP_URL = "https://botupgraid.onrender.com"

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает на вебхуках.")

# Эхо
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

# Flask роут для получения апдейтов (вебхук)
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        application.create_task(application.update_queue.put(update))
        return "OK"
    else:
        abort(405)

# Роут для установки вебхука
@app.route("/set_webhook")
def set_webhook():
    webhook_url = f"{APP_URL}/webhook/{TOKEN}"
    success = bot.setWebhook(webhook_url)
    return f"Webhook установлен: {success}"

# Роут для удаления вебхука
@app.route("/delete_webhook")
def delete_webhook():
    success = bot.deleteWebhook()
    return f"Webhook удалён: {success}"

if __name__ == "__main__":
    import asyncio
    # Запускаем в отдельном таске бота
    loop = asyncio.get_event_loop()
    loop.create_task(application.initialize())
    loop.create_task(application.start())
    try:
        app.run(host="0.0.0.0", port=10000)
    finally:
        loop.run_until_complete(application.stop())
        loop.run_until_complete(application.shutdown())