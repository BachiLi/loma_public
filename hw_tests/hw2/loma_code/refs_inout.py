def refs_inout(x : float, y : Ref[float], z : Ref[float]):
    y = y * 5.0 - x * x
    z = 2.0 * y
    y = x + z

d_refs_inout = rev_diff(refs_inout)
