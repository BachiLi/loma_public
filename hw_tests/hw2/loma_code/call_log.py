def call_log(x : In[float]) -> float:
    return log(x)

d_call_log = rev_diff(call_log)
