import requests

API_BASE_URL = "https://api.exchangerate.host"

def get_latest_rates(base: str = "USD") -> dict:
    """Получает актуальные курсы валют относительно base."""
    try:
        response = requests.get(f"{API_BASE_URL}/latest", params={"base": base.upper()}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("rates"):
            raise ValueError("Нет данных о курсах")
        return data
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Ошибка подключения к API: {e}")
    except ValueError as e:
        raise ValueError(f"Ошибка данных: {e}")

def get_historical_rate(date: str, base: str = "USD", target: str = "EUR") -> float:
    """Получает курс валюты на указанную дату."""
    try:
        response = requests.get(f"{API_BASE_URL}/{date}", params={"base": base.upper()}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["rates"][target.upper()]
    except Exception as e:
        raise ValueError(f"Не удалось получить исторический курс: {e}")