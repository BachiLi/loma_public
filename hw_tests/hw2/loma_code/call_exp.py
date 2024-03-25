def call_exp(x : In[float]) -> float:
    return exp(x)

d_call_exp = rev_diff(call_exp)
