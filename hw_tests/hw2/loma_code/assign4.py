def assign4(x : In[float], y : In[float]) -> float:
    z : float
    z = 2.5 * x - 3.0 * y
    z = z * z + z * x * y + z
    return z

d_assign4 = rev_diff(assign4)
