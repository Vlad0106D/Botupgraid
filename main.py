import logging
import asyncio
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

application = ApplicationBuilder().token(TOKEN).build()

enabled_strategies = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой трейдинг-бот. Используй /help для списка команд.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь по командам\n"
        "/strategy - Показать активные стратегии\n"
        "/strategy enable <название> - Включить стратегию\n"
        "/strategy disable <название> - Отключить стратегию\n"
    )
    await update.message.reply_text(text)

async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        if not enabled_strategies:
            await update.message.reply_text("Нет активных стратегий.")
        else:
            await update.message.reply_text(
                "Активные стратегии:\n" + "\n".join(enabled_strategies)
            )
        return

    action = args[0].lower()
    if action not in ("enable", "disable"):
        await update.message.reply_text("Используйте: /strategy enable <название> или /strategy disable <название>")
        return
    if len(args) < 2:
        await update.message.reply_text("Пожалуйста, укажите название стратегии.")
        return

    strategy_name = args[1].lower()
    if action == "enable":
        enabled_strategies.add(strategy_name)
        await update.message.reply_text(f"Стратегия '{strategy_name}' включена.")
    else:
        if strategy_name in enabled_strategies:
            enabled_strategies.remove(strategy_name)
            await update.message.reply_text(f"Стратегия '{strategy_name}' отключена.")
        else:
            await update.message.reply_text(f"Стратегия '{strategy_name}' не была активна.")

def setup_handlers():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("strategy", strategy_command))

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        # Запускаем асинхронную обработку в фоне
        asyncio.create_task(process_update_async(update))
        return "ok"
    else:
        abort(405)

async def process_update_async(update: Update):
    try:
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")

if __name__ == "__main__":
    setup_handlers()

    import os
    webhook_url = os.getenv("WEBHOOK_URL", "https://botupgraid.onrender.com/webhook")

    async def main():
        # Устанавливаем вебхук
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")

        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        config = Config()
        config.bind = ["0.0.0.0:10000"]
        logger.info("Запуск Flask-сервера...")
        await serve(app, config)

    asyncio.run(main())