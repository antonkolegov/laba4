import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from api_client import get_historical_rate

def generate_chart(base: str, target: str, days: int = 7) -> str:
    """
    Генерирует график изменения курса за последние N дней
    """
    dates = []
    rates = []

    for i in range(days):
        date = (datetime.today() - timedelta(days=days - i)).strftime("%Y-%m-%d")
        try:
            rate = get_historical_rate(date, base, target)
            dates.append(date)
            rates.append(rate)
        except:
            continue  # Пропускаем дни без данных

    if not rates:
        raise ValueError("Нет данных для построения графика")

    plt.figure(figsize=(10, 5))
    plt.plot(dates, rates, marker='o')
    plt.title(f"Курс {base}/{target} за последние {days} дней")
    plt.xlabel("Дата")
    plt.ylabel("Курс")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"chart_{base}_{target}.png"
    plt.savefig(filename)
    plt.close()
    return filename