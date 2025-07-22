import os
import logging
from quart import Quart, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN", "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://yourapp.onrender.com

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Quart(__name__)
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# --- Обработчики команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я готов к работе.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Запуск бота\n"
        "/help - Помощь\n"
        "/check - Проверка стратегий"
    )
    await update.message.reply_text(help_text)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь добавь логику анализа, сейчас просто пример
    await update.message.reply_text("Проверка стратегий: активных стратегий нет.")

# Регистрируем команды
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("check", check))

# --- Webhook endpoint ---

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        json_data = await request.get_json()
        update = Update.de_json(json_data, bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Ошибка при обработке update: {e}")
    return jsonify({"status": "ok"})

# --- Простой роут для проверки работы сервера ---

@app.route('/')
async def index():
    return "Бот запущен и работает!"

# --- Установка webhook и запуск сервера ---

async def set_webhook():
    if not WEBHOOK_URL:
        logging.error("Переменная окружения WEBHOOK_URL не задана")
        return
    webhook_full_url = f"{WEBHOOK_URL}/webhook"
    await bot.set_webhook(webhook_full_url)
    logging.info(f"Webhook установлен на {webhook_full_url}")

async def main():
    await set_webhook()
    port = int(os.getenv("PORT", 5000))
    await app.run_task(host="0.0.0.0", port=port)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())