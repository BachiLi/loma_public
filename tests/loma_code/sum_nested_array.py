def sum_nested_array(arr : Array[Array[int]], size : Array[int], n : int) -> int:
    s : int = 0
    i : int = 0
    while (i < n, max_iter := 100):
        j : int = 0
        while (j < size[i], max_iter := 100):
            s = s + arr[i][j]
            j = j + 1
        i = i + 1
    return s
