def calculate_result(numbers):
    total = 0

    for number in numbers:
        if number > 50:
            total += number * 2
        elif number > 20:
            total += number
        else:
            total -= number

    return total


def check_status(value):
    if value > 100:
        return "Very High"
    elif value > 80:
        return "High"
    elif value > 50:
        return "Medium"
    else:
        return "Low"


numbers = [10, 25, 60, 90, 15]
result = calculate_result(numbers)
status = check_status(result)

print("Result:", result)
print("Status:", status)
def calculate_average(numbers):
    if not numbers:
        return 0

    total = sum(numbers)
    return total / len(numbers)


def find_maximum(numbers):
    if not numbers:
        return 0

    maximum = numbers[0]

    for number in numbers:
        if number > maximum:
            maximum = number

    return maximum
def calculate_average(numbers):
    total = 0

    for number in numbers:
        total += number

    if len(numbers) > 0:
        return total / len(numbers)

    return 0