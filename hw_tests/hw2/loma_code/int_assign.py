def int_assign(x : float, y : int) -> float:
    z : int = y
    w : float = z * x
    z = 6
    return w * z * x + y - 1

d_int_assign = rev_diff(int_assign)
