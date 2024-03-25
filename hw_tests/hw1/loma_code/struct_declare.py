class Foo:
    a : float
    b : int

def struct_declare(f : In[Foo]) -> Foo:
    foo : Foo = f
    foo.a = foo.a * 2
    return foo

d_struct_declare = fwd_diff(struct_declare)
