class Foo:
    x : int
    b : Bar
    bs : Array[Bar, 3]

class Bar:
    y : float
    z : int

def struct_init_zero() -> int:
    f : Foo
    return f.x + f.b.y + f.b.z + f.bs[0].y + f.bs[1].z + f.bs[2].y
