class Foo:
    x : float
    y : Bar

class Bar:
    z : int
    w : float

def nested_struct_input(foo : Foo) -> float:
    b : Bar
    b.z = 5
    b.w = 3
    return (foo.x + foo.y.z + foo.y.w + b.z) * b.w

d_nested_struct_input = rev_diff(nested_struct_input)
