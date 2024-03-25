def call_pow(x : In[float], y : In[float]) -> float:
    return pow(x, y)

d_call_pow = fwd_diff(call_pow)
