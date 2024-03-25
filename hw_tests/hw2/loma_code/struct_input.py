class Foo:
    x : float
    y : int
    z : float

def struct_input(foo : In[Foo]) -> float:
    w : int = 5
    return w * foo.x + foo.y + foo.x * foo.z - 1

d_struct_input = rev_diff(struct_input)
