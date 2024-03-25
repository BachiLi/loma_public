@simd
def parallel_add(x : In[Array[int]],
                 y : In[Array[int]],
                 z : Out[Array[int]]):
    i : int = thread_id()
    z[i] = x[i] + y[i]
