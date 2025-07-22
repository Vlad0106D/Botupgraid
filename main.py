import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Активные стратегии
active_strategies = set()

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-приложение
app = Flask(__name__)

# Telegram Application (без start/initialize)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

# ========== Обработчики ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я трейдинг-бот. Введи /help для списка команд.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 *Команды трейдинг-бота:*\n\n"
        "/start — запустить бота\n"
        "/help — помощь\n"
        "/strategy — список включённых стратегий\n"
        "/strategy_on <название> — включить стратегию\n"
        "/strategy_off <название> — отключить стратегию"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if active_strategies:
        strategies = "\n".join(f"✅ {s}" for s in active_strategies)
        await update.message.reply_text(f"🔧 Активные стратегии:\n{strategies}")
    else:
        await update.message.reply_text("Нет активных стратегий.")

async def strategy_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = context.args[0]
        active_strategies.add(name)
        await update.message.reply_text(f"Стратегия '{name}' включена.")
    else:
        await update.message.reply_text("Укажи название стратегии: /strategy_on <название>")

async def strategy_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = context.args[0]
        if name in active_strategies:
            active_strategies.remove(name)
            await update.message.reply_text(f"Стратегия '{name}' отключена.")
        else:
            await update.message.reply_text(f"Стратегия '{name}' не была включена.")
    else:
        await update.message.reply_text("Укажи название стратегии: /strategy_off <название>")

# ========== Flask Webhook ==========
@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
    return "OK"

# ========== Запуск ==========
async def main():
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help_command))
    app_telegram.add_handler(CommandHandler("strategy", strategy))
    app_telegram.add_handler(CommandHandler("strategy_on", strategy_on))
    app_telegram.add_handler(CommandHandler("strategy_off", strategy_off))

    await app_telegram.bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен")

    # Flask через Hypercorn
    import hypercorn.asyncio
    from hypercorn.config import Config
    config = Config()
    config.bind = ["0.0.0.0:10000"]
    logger.info("Запуск Flask-сервера...")
    await hypercorn.asyncio.serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())