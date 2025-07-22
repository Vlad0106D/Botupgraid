import logging
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

# Инициализируем приложение Telegram бота
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Структура для хранения включенных стратегий
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

@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, app_telegram.bot)
        try:
            await app_telegram.process_update(update)
        except Exception as e:
            logger.error(f"Ошибка при обработке update: {e}")
        return "ok"
    else:
        abort(405)

def setup_handlers():
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help_command))
    app_telegram.add_handler(CommandHandler("strategy", strategy_command))

if __name__ == "__main__":
    setup_handlers()
    # Установка webhook
    webhook_url = "https://botupgraid.onrender.com/webhook"
    import asyncio
    async def main():
        await app_telegram.bot.set_webhook(webhook_url)
        logger.info("Webhook установлен: True")
        # Запуск Flask через Hypercorn
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        config = Config()
        config.bind = ["0.0.0.0:10000"]
        logger.info("Запуск Flask-сервера...")
        await serve(app, config)

    asyncio.run(main())