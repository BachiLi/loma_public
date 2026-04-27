class Foo:
    ival : int
    fval : float

def local_array_struct_init() -> float:
    arr : Array[Foo, 30]
    return arr[5].ival + arr[4].fval
