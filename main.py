import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import random

TOKEN = "7753750626:AAECEmbPksDUXV1KXrAgwE6AO1wZxdCMxVo"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Список активных стратегий
ACTIVE_STRATEGIES = ["Комплексный технический анализ"]

# Список торгуемых пар
TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Бот запущен и готов к работе. Введите /help для списка команд.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — запуск бота\n"
        "/help — справка\n"
        "/strategy — список активных стратегий\n"
        "/check — выполнить технический анализ и найти сигналы"
    )

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ACTIVE_STRATEGIES:
        msg = "📈 Активные стратегии:\n" + "\n".join(f"- {s}" for s in ACTIVE_STRATEGIES)
    else:
        msg = "❌ Нет активных стратегий."
    await update.message.reply_text(msg)

# Заглушки для индикаторов (будут заменены на реальные данные)
def mock_rsi():
    value = random.randint(10, 90)
    if value > 70:
        return "RSI: Перекупленность (SHORT)", "short"
    elif value < 30:
        return "RSI: Перепроданность (LONG)", "long"
    return "RSI: Нейтрально", "none"

def mock_ma():
    direction = random.choice(["long", "short", "none"])
    return f"MA: Направление {direction.upper()}", direction

def mock_momentum():
    direction = random.choice(["long", "short", "none"])
    return f"Momentum: {direction.upper()}", direction

def mock_bollinger():
    direction = random.choice(["long", "short", "none"])
    return f"Bollinger: {direction.upper()}", direction

def mock_oi():
    direction = random.choice(["long", "short", "none"])
    return f"OI: {direction.upper()}", direction

def aggregate_signals(signals):
    long_count = signals.count("long")
    short_count = signals.count("short")
    if long_count > short_count and long_count >= 3:
        return "LONG"
    elif short_count > long_count and short_count >= 3:
        return "SHORT"
    return "NONE"

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Комплексный технический анализ:\n"
    for pair in TRADING_PAIRS:
        indicators = []
        directions = []

        rsi_text, rsi_dir = mock_rsi()
        indicators.append(rsi_text)
        directions.append(rsi_dir)

        ma_text, ma_dir = mock_ma()
        indicators.append(ma_text)
        directions.append(ma_dir)

        mom_text, mom_dir = mock_momentum()
        indicators.append(mom_text)
        directions.append(mom_dir)

        boll_text, boll_dir = mock_bollinger()
        indicators.append(boll_text)
        directions.append(boll_dir)

        oi_text, oi_dir = mock_oi()
        indicators.append(oi_text)
        directions.append(oi_dir)

        signal = aggregate_signals(directions)
        msg += f"\n▶️ Пара: {pair}\n" + "\n".join(indicators) + f"\n📍 Итоговый сигнал: *{signal}*\n"
    await update.message.reply_markdown(msg)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("strategy", strategy))
    app.add_handler(CommandHandler("check", check))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())