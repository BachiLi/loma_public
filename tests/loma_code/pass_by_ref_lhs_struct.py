class Foo:
    x : int
    y : float

def pass_by_ref_lhs_struct(f : Out[Foo]):
    f.x = 5
