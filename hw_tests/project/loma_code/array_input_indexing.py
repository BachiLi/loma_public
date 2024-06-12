@openMpi
def array_input_indexing(x : In[Array[float]], v : In[int], c : In[float]) -> float:
    return x[v] + x[float2int(c)] + x[2 * v] + x[2 * float2int(c)]

d_array_input_indexing = fwd_diff(array_input_indexing)
