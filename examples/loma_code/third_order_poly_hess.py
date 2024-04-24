def third_order_poly(x : In[float], y : In[float]) -> float:
    x3_term : float = 0.05 * x * x * x
    y3_term : float = 0.03 * y * y * y
    x2y_term : float = -0.02 * x * x * y
    xy2_term : float = -0.04 * x * y * y
    x2_term : float = 1.2 * x * x
    y2_term : float = 0.6 * y * y
    xy_term : float = -0.5 * x * y
    x_term : float = 0.3 * x
    y_term : float = -0.2 * y
    c_term : float = -0.15
    return x3_term + \
        y3_term + \
        x2y_term + \
        xy2_term + \
        x2_term + \
        y2_term + \
        xy_term + \
        x_term + \
        y_term +  \
        c_term

fwd_third_order_poly = fwd_diff(third_order_poly)

def grad_third_order_poly(x : In[float], y : In[float], gx : Out[float], gy : Out[float]):
    d_x : Diff[float]
    d_x.val = x
    d_x.dval = 1.0
    d_y : Diff[float]
    d_y.val = y
    d_y.dval = 0.0

    ret_x : Diff[float] = fwd_third_order_poly(d_x, d_y)
    gx = ret_x.dval
    d_x.dval = 0.0
    d_y.dval = 1.0
    ret_y : Diff[float] = fwd_third_order_poly(d_x, d_y)
    gy = ret_y.dval

rev_grad_poly = rev_diff(grad_third_order_poly)

def hess_third_order_poly(x : In[float], y : In[float],
                          hxx : Out[float], hxy : Out[float], hyy : Out[float]):
    rev_grad_poly(x, hxx, y, hxy, 1.0, 0.0)
    rev_grad_poly(x, hxy, y, hyy, 0.0, 1.0)
