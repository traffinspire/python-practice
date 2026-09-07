import requests 
from datetime import datetime, timezone

# Получаем список валют, которые поддерживает API
currencies_url="https://open.er-api.com/v6/latest/USD"

currencies_response = requests.get(currencies_url)
currencies_data = currencies_response.json()

# Берем только коды валют из ответа API и сортируем их по алфавиту
currencies = sorted(currencies_data["rates"].keys())

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

    # Получаем актуальные курсы относительно выбранной исходной валюты
    url = f"https://open.er-api.com/v6/latest/{from_currency}"

    response = requests.get(url)
    data = response.json()

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
    update_date = datetime.fromtimestamp(
        data["time_last_update_unix"],
        tz=timezone.utc,
    ).strftime("%d.%m.%Y")

    # Показываем пользователю курс и дату его обновления
    print(f"Актуальный курс обмена "
        f"{from_currency} -> {to_currency}: {rate:.3f}"
    )

    print(f"Дата обновления курса: {update_date}")

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
        f"{amount:.2f} {from_currency} = "
        f"{result:.2f} {to_currency}"
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

        