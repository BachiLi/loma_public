def subtract(x : In[float], y : In[float]) -> float:
    return x - y

d_subtract = fwd_diff(subtract)
