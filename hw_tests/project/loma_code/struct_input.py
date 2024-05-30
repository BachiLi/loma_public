class Foo:
    x : float
    y : int

@openMpi
def struct_input(foo : In[Foo]) -> float:
    z : int = 5
    return z * foo.x + foo.y - 1

d_struct_input = fwd_diff(struct_input)
