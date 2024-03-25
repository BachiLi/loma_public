class Foo:
    x : int
    b : Array[Bar]

class Bar:
    y : int

def struct_in_array_in_struct(arr : In[Array[Foo]]) -> int:
    return arr[0].x + arr[1].b[0].y
