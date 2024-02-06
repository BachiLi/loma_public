def poly(x : In[float]):
	return 3 * x * x * x * x + 5 * x * x + 10

d_poly = fwd_diff(poly)

def d_poly_dx(x : In[float]):
	return d_poly(x, 1.0).dval
