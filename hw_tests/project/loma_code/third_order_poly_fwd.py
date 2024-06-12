@openMpi
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

d_fwd_third_order_poly = fwd_diff(third_order_poly)
