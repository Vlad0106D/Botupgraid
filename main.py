import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start\n/help\n/strategies")

async def strategies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нет активных стратегий.")

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("strategies", strategies))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Telegram bot started")

    # Ждем пока приложение не остановится (т.е. вечно)
    await app.updater.idle()
    await app.stop()
    await app.shutdown()

async def handle(request):
    return web.Response(text="Bot is running!")

async def run_webserver():
    app = web.Application()
    app.router.add_get('/', handle)

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Webserver running on port {port}")

    # Вечный цикл, чтобы веб-сервер не останавливался
    while True:
        await asyncio.sleep(3600)

async def main():
    # Запускаем веб-сервер и бота параллельно
    bot_task = asyncio.create_task(run_bot())
    web_task = asyncio.create_task(run_webserver())

    await asyncio.gather(bot_task, web_task)

if __name__ == "__main__":
    # Не вызываем asyncio.run, т.к. в run_bot уже внутри event loop
    asyncio.run(main())