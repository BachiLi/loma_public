def sum_nested_array(arr : In[Array[Array[float]]]) -> float:
    s : float = 0
    s = s + arr[0][0] * arr[0][0]
    s = s + arr[0][1] * arr[0][1]
    s = s + arr[0][2] * arr[0][2]
    s = s + arr[1][0] * arr[1][0]
    s = s + arr[1][1] * arr[1][1]
    s = s + arr[2][0] * arr[2][0]
    return s

d_sum_nested_array = rev_diff(sum_nested_array)
