class Foo:
    a : float
    b : int

def struct_output(x : In[float], y : In[int]) -> Foo:
    foo : Foo
    foo.a = x + y * x
    foo.b = y - x
    return foo

d_struct_output = rev_diff(struct_output)
