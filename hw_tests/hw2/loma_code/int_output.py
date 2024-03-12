def int_output(x : float, y : int) -> int:
    z : int = 5
    return z * x + y - 1

d_int_output = rev_diff(int_output)
