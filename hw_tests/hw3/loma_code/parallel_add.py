@simd
def parallel_add(x : In[Array[float]],
                 y : In[Array[float]],
                 z : Out[Array[float]]):
    i : int = thread_id()
    z[i] = x[i] + y[i]

rev_parallel_add = rev_diff(parallel_add)
