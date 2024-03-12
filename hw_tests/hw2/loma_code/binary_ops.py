def plus(x : float, y : float) -> float:
    return x + y

def subtract(x : float, y : float) -> float:
    return x - y

def multiply(x : float, y : float) -> float:
    return x * y

def divide(x : float, y : float) -> float:
    return x / y

d_plus = rev_diff(plus)
d_subtract = rev_diff(subtract)
d_multiply = rev_diff(multiply)
d_divide = rev_diff(divide)
