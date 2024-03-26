def three_level_while_loop(x : In[float], n : In[int]) -> float:
    i : int = 0
    j : int = 0
    k : int = 0
    z : float = x

    while (i < n, max_iter := 10):
        j = 0
        while (j < n, max_iter := 10):
            k = 0
            while (k < n, max_iter := 10):
                z = z + x * x
                k = k + 1
            j = j + 1
        i = i + 1
    return z

rev_three_level_while_loop = rev_diff(three_level_while_loop)
