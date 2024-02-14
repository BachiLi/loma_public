class Foo:
    x : int
    y : float

def pass_by_ref_rhs_struct(f : Ref[Foo]) -> int:
    return f.x
