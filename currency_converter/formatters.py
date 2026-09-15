from datetime import datetime, timezone



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
