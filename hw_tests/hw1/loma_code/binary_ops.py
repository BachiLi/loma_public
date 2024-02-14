def plus(x : float, y : float) -> float:
    return x + y

def subtract(x : float, y : float) -> float:
    return x - y

def multiply(x : float, y : float) -> float:
    return x * y

def divide(x : float, y : float) -> float:
    return x / y

d_plus = fwd_diff(plus)
d_subtract = fwd_diff(subtract)
d_multiply = fwd_diff(multiply)
d_divide = fwd_diff(divide)
