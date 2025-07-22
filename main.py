import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
import httpx

# === Настройки ===
BOT_TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"
PORT = 10000

# === Логирование ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask-приложение ===
app = Flask(__name__)
app_telegram = None  # будет инициализирован позже


# === Команды бота ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я трейдинг-бот 📈\n"
        "Я буду присылать сигналы и рыночные отчёты.\n"
        "Напиши /help, чтобы увидеть список доступных команд."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 Доступные команды:\n"
        "/start – Начать работу с ботом\n"
        "/help – Справка по командам\n"
        "/strategy – Управление торговыми стратегиями (вкл/выкл)\n"
        "/testlong – Отправить тестовый сигнал Long\n"
        "/testshort – Отправить тестовый сигнал Short"
    )


# === Flask endpoint для Telegram webhook ===
@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "ok", 200


# === Установка webhook ===
async def set_webhook():
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        params = {"url": WEBHOOK_URL}
        response = await client.post(url, params=params)
        result = response.json()
        logger.info(f"Webhook установлен: {result.get('ok')}")


# === Запуск Telegram-бота и Flask ===
async def main():
    global app_telegram

    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help_command))

    # Инициализация Telegram-бота
    await app_telegram.initialize()
    await set_webhook()
    logger.info("Webhook установлен ✅")

    # Запуск Flask через Hypercorn (если нужен локально)
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    logger.info("Запуск Flask-сервера через Hypercorn...")
    await serve(app, config)


# === Точка входа ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановлено пользователем.")