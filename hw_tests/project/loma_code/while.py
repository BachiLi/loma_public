@openMpi
def while_loop(x : In[float], n : In[int]) -> float:
    i : int = 0
    z : float = x
    while (i < n, max_iter := 1000000000):
        i = i + 1
        z = i
    return z

d_fwd_while_loop = fwd_diff(while_loop)