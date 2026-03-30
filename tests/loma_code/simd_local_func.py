def add(x : In[int], y : In[int]) -> float:
    return x + y

@simd
def simd_local_func(x : In[Array[int]],
                    y : In[Array[int]],
                    z : Out[Array[int]]):
    i : int = thread_id()
    z[i] = add(x[i], y[i])
