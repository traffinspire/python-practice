import json
import requests
from datetime import datetime, timezone


# Выполняет расчет конвертации валюты
def convert_amount(amount, rate):
    return amount * rate


# Получает актуальные курсы валют из кеша или API
def get_currency_data(from_currency, rates_cache, cache_file):
    current_time = datetime.now(timezone.utc).timestamp()

    # Возвращаем данные из кеша, если они еще актуальны
    if (
        from_currency in rates_cache
        and current_time
        < rates_cache[from_currency]["time_next_update_unix"]
    ):
        return rates_cache[from_currency], "cache"

    # Если кеш устарел, запрашиваем новые данные и сохраняем их
    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()

    rates_cache[from_currency] = data 

    with open(cache_file, "w", encoding="utf-8") as file:
        json.dump(
            rates_cache,
            file,
            ensure_ascii=False,
            indent=4,
        )

    return data, "api"


# Получает курс целевой валюты
def get_rate(data, to_currency):
    return data["rates"][to_currency]


# Загружает кеш курсов валют с диска
def load_cache(cache_file):
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


# Получает данные для начального списка валют
def get_currencies_data(rates_cache, cache_file):
    current_time = datetime.now(timezone.utc).timestamp()

    # Ищем любые актуальные данные в кеше
    for cached_currency, cached_data in rates_cache.items():
        if (
            cached_data.get("result") == "seccess"
            and "rates" in cached_data
            and current_time
            < cached_data.get("time_next_update_unix", 0)
        ):
            return cached_data, "cache", cached_currency

    # Если свежего кеша нет, обновляем одну из валют
    bootstrap_currency = next(iter(rates_cache), "USD")

    data, source = get_currency_data(
        bootstrap_currency,
        rates_cache,
        cache_file,
    )

    return data, source, bootstrap_currency


# Ищет курсы по введенной части кода
def find_currencies(currencies, search):
    return[
        currency
        for currency in currencies
        if search in currency
    ]


# Получает отсортированный список поддерживаемых валют
def get_supported_currencies(data):
    return sorted(data["rates"].keys())









