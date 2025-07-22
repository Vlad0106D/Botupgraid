import logging
import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI
import uvicorn

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# FastAPI app для Render (чтобы порт был занят)
app_fastapi = FastAPI()

@app_fastapi.get("/")
async def root():
    return {"status": "ok"}

# Telegram ботовские хендлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Напиши /check для проверки.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда /check сработала — бот живой!")

async def main():
    # Создаем Telegram Application
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем команды
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("check", check))

    # Запускаем Telegram polling и веб-сервер FastAPI параллельно
    # uvicorn.run блокирующий, поэтому запускаем его через asyncio.create_task и uvicorn.Server
    config = uvicorn.Config(app_fastapi, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    telegram_task = asyncio.create_task(telegram_app.run_polling())
    uvicorn_task = asyncio.create_task(server.serve())

    print("✅ Бот запущен и веб-сервер на порту 8000 работает")

    # Ждем оба таска (бот и веб-сервер)
    await asyncio.gather(telegram_task, uvicorn_task)

if __name__ == "__main__":
    asyncio.run(main())