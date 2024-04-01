def nested_array_output(arr : Out[Array[Array[int]]], size : In[Array[int]], n : In[int]):
    inc : int = 1
    i : int = 0
    j : int = 0
    while (i < n, max_iter := 100):
        j = 0
        while (j < size[i], max_iter := 100):
            arr[i][j] = inc
            inc = inc + 1
            j = j + 1
        i = i + 1
