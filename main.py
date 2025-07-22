from flask import Flask, request, jsonify
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from hypercorn.asyncio import serve
from hypercorn.config import Config

app = Flask(__name__)

BOT_TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот запущен и готов к работе.")

application.add_handler(CommandHandler("start", start))

# Async webhook endpoint
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return jsonify({"ok": True})

async def main():
    await application.initialize()
    await application.start()
    # Здесь можно убрать polling, если используешь webhook
    # await application.updater.start_polling()

    config = Config()
    config.bind = ["0.0.0.0:10000"]
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())