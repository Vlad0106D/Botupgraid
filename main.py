import logging
import asyncio
from quart import Quart, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Твой Telegram Bot токен
TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Quart-приложение
app = Quart(__name__)

# Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# Список активных стратегий
enabled_strategies = set()

# Команды
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

# Webhook обработчик
@app.post("/webhook")
async def webhook():
    try:
        data = await request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке update: {e}")
        return "error", 500
    return "ok"

# Запуск
if __name__ == "__main__":
    async def main():
        # Хендлеры
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("strategy", strategy_command))

        # Установка вебхука
        webhook_url = "https://botupgraid.onrender.com/webhook"
        await application.initialize()
        await application.bot.set_webhook(webhook_url)
        logger.info("Webhook установлен")

        # Запуск Quart
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        config = Config()
        config.bind = ["0.0.0.0:10000"]
        await serve(app, config)

    asyncio.run(main())