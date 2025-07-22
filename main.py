import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, \
    Dispatcher, aiohttp as tg_aiohttp

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"
BOT_URL = "https://your_render_domain.onrender.com"  # замените на ваш публичный URL

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот на webhook.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /check пока не реализована.")

async def handle(request):
    # Получаем объект update из POST-запроса Telegram
    bot = request.app['bot']
    dispatcher = request.app['dispatcher']
    json_data = await request.json()
    update = Update.de_json(json_data, bot)
    await dispatcher.process_update(update)
    return web.Response()

async def on_startup(app):
    bot = app['bot']
    # Устанавливаем webhook (с HTTPS)
    await bot.set_webhook(f"{BOT_URL}/webhook")
    logging.info("Webhook установлен")

async def on_cleanup(app):
    bot = app['bot']
    await bot.delete_webhook()
    logging.info("Webhook удален")

async def init_app():
    app = web.Application()
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher(bot, None, workers=4, use_context=True)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check", check))

    app['bot'] = bot
    app['dispatcher'] = dispatcher

    app.router.add_post('/webhook', handle)

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    return app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app = asyncio.run(init_app())
    web.run_app(app, port=port)