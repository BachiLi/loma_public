def identity(x : float) -> float:
    return x

d_identity = fwd_diff(identity)
