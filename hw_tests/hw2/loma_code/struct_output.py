class Foo:
    a : float
    b : int

def struct_output(x : float, y : int) -> Foo:
    foo : Foo
    foo.a = x + y * x
    foo.b = y - x
    return foo

d_struct_output = rev_diff(struct_output)
