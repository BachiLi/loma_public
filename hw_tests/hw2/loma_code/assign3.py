def assign3(x : In[float], y : In[float]) -> float:
    z : float
    z = 2.5 * x - 3.0 * y
    z = x * y
    return z

d_assign3 = rev_diff(assign3)
