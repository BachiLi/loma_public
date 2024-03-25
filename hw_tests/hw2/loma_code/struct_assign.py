class Foo:
    a : float
    b : int

def struct_assign(f : In[Foo]) -> Foo:
    foo : Foo
    foo = f
    foo.a = foo.a * 2
    return foo

d_struct_assign = rev_diff(struct_assign)
