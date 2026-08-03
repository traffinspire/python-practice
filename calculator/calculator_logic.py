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