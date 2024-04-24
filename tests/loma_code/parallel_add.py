#@simd
def parallel_add(x : In[Array[int]],
                 y : In[Array[int]],
                 z : Out[Array[int]]):
    #i : int = thread_id()
    #z[i] = x[i] + y[i]
    z[0] = 5
    z[1] = 6
    z[2] = 7