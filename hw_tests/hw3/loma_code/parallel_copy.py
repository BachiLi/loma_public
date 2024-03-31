@simd
def parallel_copy(x : In[float],
                  z : Out[Array[float]]):
    i : int = thread_id()
    z[i] = x

rev_parallel_copy = rev_diff(parallel_copy)
