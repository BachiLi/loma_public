def array_input_indexing(x : Array[float], i : int, j : float) -> float:
    return x[i] + x[float2int(j)] + x[2 * i] + x[2 * float2int(j)]

d_array_input_indexing = fwd_diff(array_input_indexing)
