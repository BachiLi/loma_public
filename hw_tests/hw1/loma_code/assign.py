def assign(x : In[float], y : In[float]) -> float:
    z : float
    z = x + y
    return z

d_assign = fwd_diff(assign)
