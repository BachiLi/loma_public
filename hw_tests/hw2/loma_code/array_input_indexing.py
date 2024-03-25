def array_input_indexing(x : In[Array[float]], i : In[int], j : In[float]) -> float:
    y : float = x[float2int(j) + 1]
    y = y * x[float2int(j) + 2]
    return x[i] * x[float2int(j)] + x[2 * i] * x[2 * float2int(j)] + y

d_array_input_indexing = rev_diff(array_input_indexing)
