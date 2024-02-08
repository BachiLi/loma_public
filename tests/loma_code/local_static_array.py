def local_static_array() -> int:
    arr : Array[int, 10]
    i : int = 0
    while (i < 10, max_iter := 10):
        arr[i] = i + 1
        i = i + 1

    i = 0
    s : int = 0
    while (i < 10, max_iter := 10):
        s = s + arr[i]
        i = i + 1
    return s
