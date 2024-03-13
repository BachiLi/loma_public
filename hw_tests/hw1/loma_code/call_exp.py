def call_exp(x : float) -> float:
    return exp(x)

d_call_exp = fwd_diff(call_exp)
