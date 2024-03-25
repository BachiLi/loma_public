def assign2(x : In[float], y : In[float]) -> float:
    z : float
    z = 2.5 * x - 3.0 * y
    z = z + x * y
    return z

d_assign2 = rev_diff(assign2)
