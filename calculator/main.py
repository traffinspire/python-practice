def get_number(promt):
    number = float(input(promt))
    return number

def get_operation():
    operation = input("Введите операцию (+, -, *, /): ")
    return operation

def calculate(first_number, operation, second_number):
    if operation == "+":
        return first_number + second_number
    elif operation == "-":
        return first_number - second_number
    elif operation == "*":
        return first_number * second_number
    elif operation == "/":
        if second_number == 0:
            return "Ошибка: Деление на ноль невозможно."
        
        return first_number / second_number
    else: 
        return "Ошибка: Недопустимая операция."

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



