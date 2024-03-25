def identity(x : In[float]) -> float:
    return x

d_identity = rev_diff(identity)
