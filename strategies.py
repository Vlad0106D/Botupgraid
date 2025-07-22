# strategies.py

from datetime import datetime

# Заглушка: функция, которая будет возвращать сигналы
def generate_signals():
    # Позже добавим анализ RSI, MA, Momentum и т.д.
    signals = {
        "BTC/USDT": "LONG",
        "ETH/USDT": "SHORT",
        "SOL/USDT": "WAIT",
        "XRP/USDT": "LONG"
    }
    explanation = {
        "BTC/USDT": "RSI перепродан + MA пересечение вверх",
        "ETH/USDT": "Momentum падает + RSI перекуплен",
        "SOL/USDT": "Нет чёткого сигнала",
        "XRP/USDT": "Bollinger breakout + рост OI"
    }

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return signals, explanation, timestamp
