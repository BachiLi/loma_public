def constant(x : In[float]) -> float:
    return 2.0

d_constant = fwd_diff(constant)
