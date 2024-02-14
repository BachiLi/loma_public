def multiple_outputs(x : float, y : Array[float], z : Array[float]):
    y[0] = x * x
    y[1] = x * x * x
    z[0] = y[0] * y[1]

d_multiple_outputs = fwd_diff(multiple_outputs)
