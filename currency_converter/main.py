import json
import requests 
from datetime import datetime, timezone
from pathlib import Path


# Форматирование курса обмена
def format_rate(value):
    if 0 < abs(value) < 0.001:
        decimals = 6

    elif abs(value) < 1:
        decimals = 4

    else:
        decimals = 2

    return f"{value:,.{decimals}f}".replace(",", " ")


# Форматирование денежных значений
def format_amount(value):
    if 0 < abs(value) < 0.01:
        decimals = 6

    elif abs(value) < 1:
        decimals = 4

    else:
        decimals = 2

    return f"{value:,.{decimals}f}".replace(",", " ")


# Форматирование даты и времени в локальном часовом поясе компьютера
def format_local_datetime(unix_timestamp):
    return (
        datetime.fromtimestamp(
            unix_timestamp,
            tz=timezone.utc,
        )
        .astimezone()
        .strftime("%d.%m.%Y %H:%M UTC%z")
    )


# Путь к файлу кеша в папке приложения
CACHE_FILE = Path(__file__).with_name("rates_cache.json")

# Загружаем сохраненный кеш, если файл уже существует
if CACHE_FILE.exists():
    with open(CACHE_FILE, "r", encoding="utf-8") as file:
        rates_cache = json.load(file)
else:
    rates_cache = {}


# Получаем текущее время для проверки актуальности кеша
current_time = datetime.now(timezone.utc).timestamp()

# Здесь храним свежие данные для получения списка валют
currencies_data = None

# Ищем любую свежую запись в кеше
for cached_currency, cached_data in rates_cache.items():
    if (
        cached_data.get("result") == "success"
        and "rates" in cached_data
        and current_time
        < cached_data.get("time_next_update_unix", 0)
    ):
        currencies_data = cached_data

        print(
            f"Список валют загружен из кеша "
            f"для {cached_currency}."
        )
        break

# Если свежих данных в кеше нет, обращаемся к API
if currencies_data is None:

    # Если кеш уже содержит валюты, обновляем первую из них 
    # Если кеш пустой, используем USD для первого запуска
    bootstrap_currency = next(iter(rates_cache), "USD")

    currencies_url = (
        f"https://open.er-api.com/v6/latest/{bootstrap_currency}"
    )

    currencies_response = requests.get(currencies_url)
    currencies_data = currencies_response.json()

    # Сохраняем полученные данные в кеш
    rates_cache[bootstrap_currency] = currencies_data

    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            rates_cache, 
            file, 
            ensure_ascii=False, 
            indent=4,
        )

    print(f"Список валют загружен из API для {bootstrap_currency}.")

# Получаем и сортируем список кодов валют
currencies = sorted(currencies_data["rates"].keys())


# Показываем, до какого момента данные считаются актуальными
cache_valid_until = format_local_datetime(
    currencies_data["time_next_update_unix"]
)

print(f"Данные актуальны до: {cache_valid_until}")


# Показываем пользователю доступные валюты
print("Доступные валюты:")
print(", ".join(currencies))


# Основной цикл программы. 
# Позволяет выполнять несколько конвертаций без перезапуска
while True:

    # Поиск и выбор исходной валюты
    while True:
        search = input("Поиск исходной валюты: ").strip().upper()

        # Ищем все валюты, в коде которых содержится введенный текст
        matches = [
            currency
            for currency in currencies
            if search in currency 
        ]

        # Если совпадений нет, предлагаем выполнить поиск еще раз
        if not matches:
            print("Валюты не найдены. Попробуйте еще раз.")
            continue

        print("Найдено:",",".join(matches))

        # Если найден только один вариант, выбираем его автоматически
        if len(matches) == 1:
            from_currency = matches[0]
            print(f"Выбрана валюта: {from_currency}")
            break

        # Если найдено несколько вариантов, пользователь выбирает нужный
        choice = input("Выберите валюту: ").strip().upper()

        if choice in matches:
            from_currency = choice
            break

        print("Выберите валюту из найденного списка.")


    # Получаем текущее время в формате Unix
    current_time = datetime.now(timezone.utc).timestamp()

    # Проверяем, есть ли валюта в кеше и не устарели ли данные
    if (
        from_currency in rates_cache
        and current_time
        < rates_cache[from_currency]["time_next_update_unix"]
    ):
        data = rates_cache[from_currency]
        print(f"Курсы валют загружены из кеша для {from_currency}.")

    # Получаем актуальные курсы относительно выбранной исходной валюты
    else:
        url = f"https://open.er-api.com/v6/latest/{from_currency}"

        response = requests.get(url)
        data = response.json()

        rates_cache[from_currency] = data

        # Сохраняем обновленный кеш на диск
        with open(CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump(
                rates_cache, 
                file, 
                ensure_ascii=False, 
                indent=4,
            )

        print(f"Курсы валют загружены из API для {from_currency}.")

    # Проверяем, смог ли API обработать код исходной валюты
    if data["result"] == "error":
        print("Ошибка: исходной валюты не существует.")
        raise SystemExit

    # Поиск и выбор целевой валюты
    while True:
        search = input("Поиск целевой валюты: ").strip().upper()

        # Ищем совпадения среди валют, поддерживаемых API
        matches = [
            currency
            for currency in currencies
            if search in currency
        ]

        # Если совпадений нет, повторяем поиск
        if not matches:
            print("Валюты не найдены. Попробуйте еще раз.")
            continue

        print("Найдено:",",".join(matches))

        # При одном совпадении выбираем валюту автоматически
        if len(matches) == 1:
            to_currency = matches[0]
            print(f"Выбрана валюта: {to_currency}")
            break

        # При нескольких совпадениях пользователь выбирает нужную валюту
        choice = input("Выберите валюту: ").strip().upper()

        if choice in matches:
            to_currency = choice
            break

        print("Выберите валюту из найденного списка.")

    # Получаем курс выбранной валютной пары
    try:
        rate = data["rates"][to_currency]

    except KeyError:
        print("Ошибка: такой валюты не существует.")
        raise SystemExit

    # Преобразуем Unix-время обновления курса
    # в привычный формат день.месяц.год
    update_date = format_local_datetime(
        data["time_last_update_unix"]
    )

    # Показываем пользователю курс и дату его обновления
    print(f"Актуальный курс обмена "
        f"{from_currency} -> {to_currency}: {format_rate(rate)}"
    )

    print(f"Дата и время обновления курса: {update_date}")

    # Получаем сумму и проверяем корректность ввода
    while True:
        try:
            amount = float(input(f"Введите сумму: {from_currency} = "))

            # Нулевая и отрицательная сумма не допускаются
            if amount <= 0:
                print(
                    "Ошибка: сумма должна быть больше нуля. "
                    "Попробуйте еще раз."
                )
                continue

            break

        except ValueError:
            print("Ошибка: сумма должна быть числом. Попробуйте еще раз.")

    # Выполняем конвертацию
    result = amount * rate

    # Выводим итоговый результат
    print(
        f"Результат конвертации: "
        f"{format_amount(amount)} {from_currency} = "
        f"{format_amount(result)} {to_currency}"
    )

    # Спрашиваем, нужно ли выполнить еще одну конвертацию
    while True:
        again = input(
            "Выполнить еще одну конвертацию? (y/n): "
        ).strip().lower()

        # Принимаем только y или n
        if again in ("y", "n"):
            break

        print("Введите 'y' для продолжения или 'n' для выхода.")

    # Завершаем основной цикл программы по команде пользователя
    if again == "n":
        print("Работа завершена.")
        break

        