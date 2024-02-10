def local_array_init_zero() -> int:
    arr : Array[int, 10]
    arr[3] = 5
    arr[7] = 8

    i : int = 0
    s : int = 0
    while (i < 10, max_iter := 10):
        s = s + arr[i]
        i = i + 1

    return s
