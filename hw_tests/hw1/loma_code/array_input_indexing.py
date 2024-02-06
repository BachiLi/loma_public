def array_input_indexing(x : In[Array[float]], i : In[int], j : In[float]) -> float:
    return x[i] + x[float2int(j)] + x[2 * i] + x[2 * float2int(j)]

d_array_input_indexing = fwd_diff(array_input_indexing)
