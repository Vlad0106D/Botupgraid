import os
import logging
from quart import Quart, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
WEBHOOK_URL = "https://botupgraid.onrender.com/webhook"

# Логирование
logging.basicConfig(level=logging.INFO)

# Quart app
app = Quart(__name__)
telegram_app = None

# 🔧 Список стратегий
default_strategies = [
    "Комплексный технический анализ",
    "Приток/отток капитала",
    "RSI + MA",
    "Momentum + Bollinger",
    "Открытый интерес + объем"
]
active_strategies = default_strategies.copy()

@app.before_serving
async def before_serving():
    global telegram_app
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(CommandHandler("strategy", strategy))
    telegram_app.add_handler(CommandHandler("addstrategy", add_strategy))
    telegram_app.add_handler(CommandHandler("removestrategy", remove_strategy))

    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook установлен.")
    await telegram_app.start()


@app.route("/", methods=["GET"])
async def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"


@app.after_serving
async def after_serving():
    await telegram_app.stop()
    await telegram_app.shutdown()


# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Используй /help для списка команд.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — запуск\n"
        "/strategy — список активных стратегий\n"
        "/addstrategy Название — добавить стратегию\n"
        "/removestrategy Название — удалить стратегию"
    )


async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not active_strategies:
        await update.message.reply_text("Нет активных стратегий.")
    else:
        strategies_text = "\n".join(f"• {s}" for s in active_strategies)
        await update.message.reply_text(f"Активные стратегии:\n{strategies_text}")


async def add_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи название стратегии. Пример: /addstrategy RSI + MA")
        return

    name = " ".join(context.args)
    if name in active_strategies:
        await update.message.reply_text(f"Стратегия '{name}' уже активна.")
    else:
        active_strategies.append(name)
        await update.message.reply_text(f"Добавлена стратегия: {name}")


async def remove_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи название стратегии. Пример: /removestrategy RSI + MA")
        return

    name = " ".join(context.args)
    if name in active_strategies:
        active_strategies.remove(name)
        await update.message.reply_text(f"Удалена стратегия: {name}")
    else:
        await update.message.reply_text(f"Стратегия '{name}' не найдена.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)