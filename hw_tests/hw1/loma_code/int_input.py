def int_input(x : float, y : int) -> float:
    z : int = 5
    return z * x + y - 1

d_int_input = fwd_diff(int_input)
