from flask import Flask
import threading
import os
from telegram.ext import Updater, CommandHandler

app = Flask(__name__)

@app.route("/")
def index():
    return "Flask работает вместе с Telegram-ботом!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def start(update, context):
    update.message.reply_text("Привет! Я твой Telegram-бот.")

def run_bot():
    TOKEN = "776505127:AAHMC24Ax14hw_3dykAXg3U0d6JDTRkzF9E"

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    run_bot()