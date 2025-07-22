import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем приложение бота
application = ApplicationBuilder().token(TOKEN).build()

# Множество для хранения включенных стратегий
enabled_strategies = set()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой трейдинг-бот. Используй /help для списка команд.")

# Команда /help
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

# Команда /strategy
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

# Регистрируем хендлеры
def setup_handlers():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("strategy", strategy_command))

if __name__ == "__main__":
    setup_handlers()
    # Запускаем бота в режиме polling
    application.run_polling()