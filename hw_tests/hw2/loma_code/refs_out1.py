def refs_out1(x : float, y : Ref[float]):
    y = x * x

d_refs_out1 = rev_diff(refs_out1)
