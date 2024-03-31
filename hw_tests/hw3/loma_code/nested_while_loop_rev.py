def nested_while_loop(x : In[float], n : In[int]) -> float:
    i : int = 0
    j : int = 0
    z : float = 0.0

    while (i < n, max_iter := 10):
        j = 0
        while (j < i, max_iter := 10):
            z = z + x * x
            j = j + 1
        i = i + 1
    return z

rev_nested_while_loop = rev_diff(nested_while_loop)
