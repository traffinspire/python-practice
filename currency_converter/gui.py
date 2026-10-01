import asyncio
import flet as ft
from pathlib import Path
from converter_logic import (
    convert_amount,
    find_currencies,
    get_currencies_data,
    get_currency_data,
    get_rate,
    get_supported_currencies,
    load_cache,
)
from formatters import (
    format_amount,
    format_rate,
    format_local_datetime,
)



# Путь к общему файлу кеша валют
CACHE_FILE = Path(__file__).with_name("rates_cache.json")


# Главная функция графического приложения
def main(page: ft.Page):
    # Заголовок окна приложения
    page.title = "Currency Converter"

    # Загружаем сохраненный кеш курсов валют
    rates_cache = load_cache(CACHE_FILE)

    # Получаем актуальные данные для списка валют
    currencies_data, source, base_currency = get_currencies_data(
        rates_cache,
        CACHE_FILE,
    )

    # Получаем отсортированный список поддерживаемых валют
    currencies = get_supported_currencies(currencies_data)

    # Выпдающий список исходной валюты с поиском
    from_currency = ft.Dropdown(
        label="Из валюты",
        hint_text="Выберите валюту",
        value=None,
        options=[
            ft.DropdownOption(
                key=currency,
                text=currency,
            )
            for currency in currencies
        ],
    )

    # Поле поиска исходной валюты
    from_search = ft.TextField(
        label="Поиск",
        width=120,

        # Только латинские буквы
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^[A-Za-z]*$",
            replacement_string="",
        ),
    )

    # Выпдающий список целевой валюты с поиском
    to_currency = ft.Dropdown(
        label="В валюту",
        hint_text="Выберите валюту",
        value=None,
        options=[
            ft.DropdownOption(
                key=currency,
                text=currency,
            )
            for currency in currencies
        ],
    )

    # Поле поиска целевой валюты
    to_search = ft.TextField(
        label="Поиск",
        width=120,

        # Только латинские буквы
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^[A-Za-z]*$",
            replacement_string="",
        ),
    )


    # Фильтрует список исходных валют при вводе текста
    def search_from_currency(e):
        search = e.control.value.strip().upper()

        # Если поле пустое, снова показываем все валюты
        if not search:
            matches = currencies

        else:
            matches = find_currencies(
                currencies,
                search,
            )

        # обновляем варианты выпадающего списка 
        from_currency.options = [
            ft.DropdownOption(
                key=currency,
                text=currency,
            )
            for currency in matches
        ]

        # Если найден один вариант, выбираем его автоматически
        if len(matches) == 1:
            from_currency.value = matches[0]
            from_currency.label = "Из валюты"

        # Если вариантов несколько или ничего не найдено,
        # очищаем старый выбор и предлагаем выбрать вариант
        elif len(matches) > 1:
            from_currency.value = None
            from_currency.label = (
                f"Выберите валюту ({len(matches)})"
            )

        # Если ничего не найдено
        else:
            from_currency.value = None
            from_currency.label = "Валюта не найдена"


    # Запускаем поиск при каждом изменении текста
    from_search.on_change = search_from_currency


    # Фильтрует список целевых валют при вводе текста
    def search_to_currency(e):
        search = e.control.value.strip().upper()

        # Если поле поиска пустое, показываем все валюты
        if not search:
            matches = currencies

        else:
            matches = find_currencies(
                currencies,
                search,
            )

        # Обновляем варианты в выпадающем списке
        to_currency.options = [
            ft.DropdownOption(
                key=currency,
                text=currency,
            )
            for currency in matches
        ]

        # Если найдена одна валюта, выбираем ее автоматически
        if len(matches) == 1:
            to_currency.value = matches[0]
            to_currency.label = "В валюту"

        # Если найдено несколько вариантов
        elif len(matches) > 1:
            to_currency.value = None
            to_currency.label = (
                f"Выберите валюту ({len(matches)})"
            )

        # Если ничего не найдено
        else:
            to_currency.value = None
            to_currency.label = "Валюта не найдена"


    # Запускаем поиск при каждом изменении текста
    to_search.on_change = search_to_currency


    # Поле для ввода суммы пользователем
    amount_field = ft.TextField(
        label="Сумма",

        # Разрешаем вводить только цифры и одну десятичную точку
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^\d*\.?\d*$",
            replacement_string="",
        ),

        # На мобильных устройствах открываем цифровую клавиатуру
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    # Текст, в котором позже будем показывать результат
    result_text = ft.Text(
        "Здесь будет результат"
    )

    # Информация об источнике и актуальности курса
    rate_info_text = ft.Text(
        ""
    )

    # Индикатор загрузки данных из API
    loading_row = ft.Row(
        controls=[
            ft.ProgressRing(
                width=20,
                height=20,
            ),
            ft.Text("Получаем актуальный курс..."),
        ],
        visible=False,
    )


    # Кнопка запуска конвертации
    convert_button = ft.Button(
        content="Конвертиовать",
    )


    # Обработчик нажатия на кнопку
    async def convert_click(e):

        # Не запускаем второй запрос, пока первый еще выполняется
        if loading_row.visible:
            return

        # Получаем выбранные валюты из выпадающих списков
        from_code = from_currency.value
        to_code = to_currency.value

        # Проверяем введеную сумму
        try:
            amount = float(amount_field.value)

            if amount <= 0:
                result_text.value = "Сумма должна быть больше нуля."
                return

        except (ValueError, TypeError):
            result_text.value = "Введите корректное число."
            return

        # Показываем пользователю, что идет получение данных
        loading_row.visible = True
        convert_button.disabled = True

        loading_row.update()
        convert_button.update()

        # Обновляем интерфейс
        page.update()


        # Запускаем блокирующий запрос вне UI-потока,
        # чтобы окно приложения не зависало
        data, source = await asyncio.to_thread(
            get_currency_data,
            from_code,
            rates_cache,
            CACHE_FILE,
        )

        # Форматируем время обновления и срок актуальности данных
        update_at = format_local_datetime(
            data["time_last_update_unix"]
        )

        valid_until = format_local_datetime(
            data["time_next_update_unix"]
        )

        # Получаем курс выбранной валютной пары
        rate = get_rate(
            data,
            to_code,
        )

        # Выполняем конвертацию
        result = convert_amount(
            amount,
            rate,
        )

        # Показываем результат пользователю
        result_text.value = (
            f"{format_amount(amount)} {from_code} = "
            f"{format_amount(result)} {to_code}\n"
            f"Курс: {format_rate(rate)}"
        )

        # Преобразуем техническое имя источника
        # в понятный текст для пользователя
        source_text = (
            "кеш"
            if source == "cache"
            else "API"
        )

        # Показываем источник и актуальность данных
        rate_info_text.value = (
            f"Источник данных: {source_text}\n"
            f"Обновлено: {update_at}\n"
            f"Актуально до: {valid_until}"
        )

        # Скрываем загрузку и снова разрешаем кнопку
        loading_row.visible = False
        convert_button.disabled = False

        loading_row.update()
        convert_button.update()

        # Обновляем весь интерфейс:
        # результат, информацию о курсе, загрузку и кнопку
        page.update()



    # Добавляем элементы интерфейса на страницу
    page.add(
        ft.Text("Конвертер валют"),
        # Поиск и выбор исходной валюты в одной строке
        ft.Row(
            controls=[
                from_search,
                from_currency,
            ]
        ),
        ft.Row(
            controls=[
                to_search,
                to_currency,
            ]
        ),
        amount_field,
        convert_button,
        loading_row,
        result_text,
        rate_info_text,
    )


    # Конвертация на кнопку Enter
    amount_field.on_submit = convert_click

    # Запускаем конвертацию по нажатию кнопки
    convert_button.on_click = convert_click



# Запускаем Flet-приложение
ft.run(main)