def call_log(x : In[float]) -> float:
    return log(x)

d_call_log = fwd_diff(call_log)
