def array_input_indexing(x : Array[float], i : int, j : float) -> float:
    y : float = x[float2int(j) + 1]
    y = y * x[float2int(j) + 2]
    return x[i] * x[float2int(j)] + x[2 * i] * x[2 * float2int(j)] + y

d_array_input_indexing = rev_diff(array_input_indexing)
