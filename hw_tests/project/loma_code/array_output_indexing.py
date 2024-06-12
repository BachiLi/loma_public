@openMpi
def array_output_indexing(x : In[float], v : In[int], c : In[float], y : Out[Array[float]]):
    y[v] = x
    y[float2int(c)] = 2 * x
    y[2 * v] = 3 * x
    y[2 * float2int(c)] = 4 * x

d_array_output_indexing = fwd_diff(array_output_indexing)
