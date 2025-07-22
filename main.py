import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import httpx

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

async def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            price = data["bitcoin"]["usd"]
            return f"🟢 BTC/USDT: ${price}"
    except Exception as e:
        return f"❌ Ошибка получения данных: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я готов к работе.\nНапиши /check чтобы получить цену BTC.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_btc_price()
    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()