def int_array_input(x : Array[float], y : Array[int]) -> float:
    return x[0] + x[1] + y[0]

d_int_array_input = fwd_diff(int_array_input)
