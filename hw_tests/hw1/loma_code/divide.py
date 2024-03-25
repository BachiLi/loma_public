def divide(x : In[float], y : In[float]) -> float:
    return x / y

d_divide = fwd_diff(divide)
