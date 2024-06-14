@openMpi
def array_input_indexing(x : In[Array[float]], v : In[int], c : In[float]) -> float:
    y : float = x[float2int(c) + 1]
    y = y * x[float2int(c) + 2]
    return x[v] * x[float2int(c)] + x[2 * v] * x[2 * float2int(c)] + y

d_array_input_indexing = rev_diff(array_input_indexing)
