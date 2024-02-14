def array_output_indexing(x : float, i : int, j : float, y : Array[float]):
    y[i] = x
    y[float2int(j)] = 2 * x
    y[2 * i] = 3 * x
    y[2 * float2int(j)] = 4 * x

d_array_output_indexing = fwd_diff(array_output_indexing)
