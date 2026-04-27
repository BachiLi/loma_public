@simd
def parallel_reduce(x : In[Array[float]],
                    z : Out[float]):
    i : int = thread_id()
    atomic_add(z, x[i])

fwd_parallel_reduce = fwd_diff(parallel_reduce)
rev_parallel_reduce = rev_diff(parallel_reduce)
