def array_input(x : In[Array[float]]) -> float:
    return 2 * x[0] + 3 * x[1] * x[1]

d_array_input = rev_diff(array_input)
