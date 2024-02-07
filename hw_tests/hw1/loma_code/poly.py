def poly(x : In[float]) -> float:
    return 3 * x * x * x * x + 5 * x * x + 10

d_poly = fwd_diff(poly)

def d_poly_dx(x : In[float]) -> float:
    d_x : Diff[float]
    d_x.val = x
    d_x.dval = 1.0
    return d_poly(d_x).dval
