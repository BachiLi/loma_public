def call_cos(x : In[float]) -> float:
    return cos(x)

d_call_cos = fwd_diff(call_cos)
