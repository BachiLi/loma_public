def array_output(x : In[float], y : Out[Array[float]]):
    y[0] = x * x
    y[1] = x * x * x

d_array_output = rev_diff(array_output)
