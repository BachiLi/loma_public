@simd
def parallel_reduce(x : In[Array[float]],
                    z : Out[float]):
    i : int = thread_id()
    atomic_add(z, x[i])

rev_parallel_reduce = rev_diff(parallel_reduce)
