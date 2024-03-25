def int_output(x : In[float], y : In[int]) -> int:
    z : int = 5
    return z * x + y - 1

d_int_output = fwd_diff(int_output)
