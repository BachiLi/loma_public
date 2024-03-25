def identity(x : In[float]) -> float:
    return x

d_identity = fwd_diff(identity)
