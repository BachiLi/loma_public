def call_cos(x : In[float]) -> float:
    return cos(x)

d_call_cos = rev_diff(call_cos)
