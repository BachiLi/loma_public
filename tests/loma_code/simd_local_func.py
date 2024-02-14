def add(x : int, y : int) -> float:
    return x + y

@simd
def simd_local_func(x : Array[int],
                    y : Array[int],
                    z : Array[int]):
    i : int = thread_id()
    z[i] = add(x[i], y[i])
