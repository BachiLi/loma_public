def call(x : In[float]) -> float:
    z0 : float = sin(x)
    z1 : float = cos(z0) + 1.0
    z2 : float = sqrt(z1)
    z3 : float = pow(z2, z1)
    z4 : float = exp(z3)
    z5 : float = log(z3 + z4)
    return z5

d_call = fwd_diff(call)
