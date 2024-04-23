@simd
def parallel_sum(x : In[Array[float]],
                 z : Out[float]):
    i : int = thread_id()
    atomic_add(z, x[i])

rev_parallel_sum = rev_diff(parallel_sum)
