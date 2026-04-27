def local_nested_array() -> int:
    arr : Array[Array[int, 8], 10]
    arr[5][5] = 5
    arr[3][6] = 4
    arr2 : Array[Array[Array[int, 2], 3], 4]
    arr2[3][2][1] = 3

    return arr[3][6] + arr2[3][2][1]
