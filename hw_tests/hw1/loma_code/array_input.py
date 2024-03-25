def array_input(x : In[Array[float]]) -> float:
    return x[0] + x[1]

d_array_input = fwd_diff(array_input)
