def refs_out(x : In[float], y : Out[float]):
    y = x * x

d_refs_out = rev_diff(refs_out)
