import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

# Простые команды для бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start\n/help\n/strategies")

async def strategies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Заглушка — пока стратегий нет
    await update.message.reply_text("Нет активных стратегий.")

async def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("strategies", strategies))

    await application.run_polling()

# Простой aiohttp сервер для Render
async def handle(request):
    return web.Response(text="Bot is running!")

async def run_webserver():
    app = web.Application()
    app.router.add_get('/', handle)

    port = int(os.environ.get("PORT", 10000))  # Render задает порт в переменной окружения
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Webserver running on port {port}")

    # Чтобы веб-сервер не завершился сразу
    while True:
        await asyncio.sleep(3600)

async def main():
    # Запускаем бота и веб-сервер параллельно
    await asyncio.gather(run_bot(), run_webserver())

if __name__ == "__main__":
    asyncio.run(main())