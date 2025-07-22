from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import logging

# Твой токен Telegram-бота
TOKEN = "6437536295:AAG9dcbMBmnDb6s0cQZCUJsIaT1skJfPO8s"

# URL твоего развернутого приложения на Render (здесь надо заменить на твой реальный)
APP_URL = "https://botupgraid.onrender.com"

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Обработчик команды /start
def start(update, context):
    update.message.reply_text("Привет! Бот работает на вебхуках.")

# Эхо-обработчик для любых текстовых сообщений
def echo(update, context):
    update.message.reply_text(f"Ты написал: {update.message.text}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

# Роут для получения апдейтов от Telegram (вебхук)
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    dispatcher.process_update(update)
    return "OK"

# Роут для установки вебхука
@app.route("/set_webhook")
def set_webhook():
    url = f"{APP_URL}/webhook/{TOKEN}"
    success = bot.setWebhook(url)
    return f"Webhook установлен: {success}"

# Роут для удаления вебхука (если нужно)
@app.route("/delete_webhook")
def delete_webhook():
    success = bot.deleteWebhook()
    return f"Webhook удалён: {success}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)