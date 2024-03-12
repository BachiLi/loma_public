def call_log(x : float) -> float:
    return log(x)

d_call_log = rev_diff(call_log)
