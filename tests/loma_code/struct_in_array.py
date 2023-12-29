class Foo:
    x : int
    y : int

def struct_in_array(arr : In[Array[Foo]]) -> int:
    return arr[0].x + arr[1].y
