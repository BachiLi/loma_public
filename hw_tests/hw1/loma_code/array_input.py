def array_input(x : Array[float]) -> float:
    return x[0] + x[1]

d_array_input = fwd_diff(array_input)
