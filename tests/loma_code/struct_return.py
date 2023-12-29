class Foo:
    x : int
    y : float

def struct_return() -> Foo:
    f : Foo
    f.x = 5
    f.y = 3.5
    return f
