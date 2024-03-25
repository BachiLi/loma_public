def declare(x : In[float], y : In[float]) -> float:
    z0 : float = x + y
    z1 : float = z0 + 5.0
    z2 : float = z1 * z0
    z3 : float = z2 / z1
    z4 : float = z3 - x
    return z4

d_declare = rev_diff(declare)
