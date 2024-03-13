def call_sqrt(x : float) -> float:
    return sqrt(x)

d_call_sqrt = fwd_diff(call_sqrt)
