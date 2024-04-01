@simd
def my_atomic_add(x : In[Array[float]],
                  z : Out[float]):
    i : int = thread_id()
    atomic_add(z, x[i])
