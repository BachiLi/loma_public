def multiply(x : In[float], y : In[float]) -> float:
    return x * y

d_multiply = fwd_diff(multiply)
