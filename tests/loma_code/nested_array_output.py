def nested_array_output(arr : Array[Array[int]], size : Array[int], n : int):
    inc : int = 1
    i : int = 0
    while (i < n, max_iter := 100):
        j : int = 0
        while (j < size[i], max_iter := 100):
            arr[i][j] = inc
            inc = inc + 1
            j = j + 1
        i = i + 1
