from datetime import datetime, timezone
from pathlib import Path
from converter_logic import (
    convert_amount,
    get_supported_currencies,
    find_currencies,
    get_currencies_data,
    get_currency_data,
    get_rate,
    load_cache,
)


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

# Загружаем кеш курсов валют с диска
rates_cache = load_cache(CACHE_FILE)


# Получаем данные для списка доступных валют
currencies_data, source, base_currency = get_currencies_data(
    rates_cache,
    CACHE_FILE,
)

# Показываем источник данных 
if source == "cache":
    print(
        f"Список валют загружен из кеша "
        f"для {base_currency}."
    )

else:
    print(
        f"Список валют загружен из API "
        f"для {base_currency}."
    )


# Получаем и сортируем список кодов валют
currencies = get_supported_currencies(currencies_data)


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
        matches = find_currencies(currencies, search)

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


    # Получаем курсы валют из кеша или API
    data, source = get_currency_data(
        from_currency,
        rates_cache,
        CACHE_FILE,
    )

    # Показываем источник полученных данных
    if source == "cache":
        print(
            f"Курсы валют загружены из кеша "
            f"для {from_currency}."
        )

    else:
        print(
            f"Курсы валют загружены из API "
            f"для {from_currency}."
        )


    # Проверяем, смог ли API обработать код исходной валюты
    if data["result"] == "error":
        print("Ошибка: исходной валюты не существует.")
        raise SystemExit

    # Поиск и выбор целевой валюты
    while True:
        search = input("Поиск целевой валюты: ").strip().upper()

        # Ищем совпадения среди валют, поддерживаемых API
        matches = find_currencies(currencies, search)

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
        rate = get_rate(data, to_currency)

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

    # Выполняем конвертацию через обновленную логику converter_logic.py
    result = convert_amount(amount, rate)

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

        