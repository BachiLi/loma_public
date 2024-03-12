def nested_array(x : Array[Array[float]]) -> float:
    return 2 * x[0][0] + 3 * x[1][1] * x[0][2]

d_nested_array = rev_diff(nested_array)
