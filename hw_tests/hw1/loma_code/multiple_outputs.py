def multiple_outputs(x : In[float], y : Out[Array[float]], z : Out[Array[float]]):
    y[0] = x * x
    y[1] = x * x * x
    z[0] = y[0] * y[1]

d_multiple_outputs = fwd_diff(multiple_outputs)
