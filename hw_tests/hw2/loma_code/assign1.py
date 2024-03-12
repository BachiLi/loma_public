def assign1(x : float, y : float) -> float:
    z : float
    z = 3.0 * x + 5.0 * y
    return z

d_assign1 = rev_diff(assign1)
