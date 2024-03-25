def assign5(x : In[float], y : In[float]) -> float:
    z : float = x * y
    w : float = z
    z = x + y
    w = w + z * z
    z = 2.0 * x
    z = z + 1.0
    z = 3.0 * z * z + w
    return z

d_assign5 = rev_diff(assign5)
