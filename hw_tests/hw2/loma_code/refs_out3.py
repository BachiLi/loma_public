def refs_out3(x : float, y : Ref[float], z : Ref[float]):
    y = x * x
    y = x * y
    z = 2.0 * y
    y = x + z

d_refs_out3 = rev_diff(refs_out3)
