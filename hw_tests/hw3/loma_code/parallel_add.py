@simd
def parallel_add(x : In[Array[float]],
                 y : In[Array[float]],
                 z : Out[Array[float]]):
    i : int = thread_id()
    z[i] = x[i] + y[i]

fwd_parallel_add = fwd_diff(parallel_add)
rev_parallel_add = rev_diff(parallel_add)
