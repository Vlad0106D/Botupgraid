import logging
import os
import httpx
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Конфигурация ===
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# === Flask-приложение ===
app = Flask(__name__)
app_telegram = None

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Добро пожаловать! Используйте /strategy чтобы просмотреть доступные стратегии.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Команды:\n/start — приветствие\n/strategy — список стратегий\n/check — ручной анализ рынка")

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Активные стратегии:\n1. Комплексный технический анализ (вручную запустить: /check)")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signals = {
        "BTC/USDT": "🔼 Long — RSI в зоне перепроданности, подтверждено пересечением MA.",
        "ETH/USDT": "🔽 Short — Momentum падает, пробиты нижние полосы Боллинджера.",
        "SOL/USDT": "⏸ Нет сигнала — показатели нейтральны.",
        "XRP/USDT": "🔼 Long — рост открытого интереса + положительный RSI."
    }

    message = "📈 Сигналы по стратегии «Комплексный технический анализ»:\n\n"
    for pair, signal in signals.items():
        message += f"{pair}: {signal}\n"

    await update.message.reply_text(message)

# === Webhook ===
@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json()
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error("Ошибка при обработке update: %s", e)
    return {"ok": True}

# === Основной запуск ===
async def main():
    global app_telegram
    app_telegram = ApplicationBuilder().token(TOKEN).build()

    # Добавляем хендлеры
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help_command))
    app_telegram.add_handler(CommandHandler("strategy", strategy))
    app_telegram.add_handler(CommandHandler("check", check))

    # Обязательно инициализируем перед использованием process_update
    await app_telegram.initialize()

    # Устанавливаем webhook
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info("Webhook установлен: %s", response.json()["ok"])

    logger.info("Telegram Application готово.")

if __name__ == "__main__":
    asyncio.run(main())

    import hypercorn.asyncio
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]
    asyncio.run(hypercorn.asyncio.serve(app, config))