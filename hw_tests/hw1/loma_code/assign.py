def assign(x : float, y : float) -> float:
    z : float
    z = x + y
    return z

d_assign = fwd_diff(assign)
