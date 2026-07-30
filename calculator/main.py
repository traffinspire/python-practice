from calculator_logic import calculate

def get_number(promt):
    number = float(input(promt))
    return number

def get_operation():
    operation = input("Введите операцию (+, -, *, /): ")
    return operation

def main():
    print("Калькулятор")

    first_number = get_number("Введите первое число: ")
    operation = get_operation()
    second_number = get_number("Введите второе число: ")
    result = calculate(first_number, operation, second_number)

    print(f"Первое число: {first_number}")
    print(f"Операция: {operation}")
    print(f"Второе число: {second_number}")
    print(f"Результат: {result}")


if __name__ == "__main__":
    main()



