def array_output_indexing(x : In[float], i : In[int], j : In[float], y : Out[Array[float]]):
    y[i] = x
    y[float2int(j)] = 2 * x
    y[2 * i] = 3 * x
    y[2 * float2int(j)] = 4 * x

d_array_output_indexing = rev_diff(array_output_indexing)
