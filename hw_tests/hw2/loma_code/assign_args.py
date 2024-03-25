def assign_args(w : In[float], x : In[float], y : In[float], z : In[float]) -> float:
    w = 5.0
    x = w + x + y + z
    y = 6.0
    z = x * x
    return z

d_assign_args = rev_diff(assign_args)
