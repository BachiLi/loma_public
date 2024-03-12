def refs_out2(x : float, y : Ref[float]):
    y = x * x
    y = x * y

d_refs_out2 = rev_diff(refs_out2)
