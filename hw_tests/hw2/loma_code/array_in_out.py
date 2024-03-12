def array_in_out(i : int, j : float, y : Array[float]):
    y[i] = y[float2int(j)] * y[2 * float2int(j)]

d_array_in_out = rev_diff(array_in_out)
