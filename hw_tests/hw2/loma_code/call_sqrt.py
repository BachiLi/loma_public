def call_sqrt(x : float) -> float:
    return sqrt(x)

d_call_sqrt = rev_diff(call_sqrt)
