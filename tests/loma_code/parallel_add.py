@simd
def parallel_add(x : Array[int],
                 y : Array[int],
                 z : Array[int]):
    i : int = thread_id()
    z[i] = x[i] + y[i]
