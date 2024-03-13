def call_sin(x : float) -> float:
    return sin(x)

d_call_sin = fwd_diff(call_sin)
