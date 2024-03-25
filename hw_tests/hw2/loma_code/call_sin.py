def call_sin(x : In[float]) -> float:
    return sin(x)

d_call_sin = rev_diff(call_sin)
