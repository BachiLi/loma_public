def while_loop(x : In[float], n : In[int]) -> float:
    i : int = 0
    z : float = x
    while (i < n, max_iter := 10):
        z = sin(z)
        i = i + 1
    return z

fwd_while_loop = fwd_diff(while_loop)
