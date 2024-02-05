def side_effect(x : In[float], y : In[float]) -> float:
    z : float
    z = x + y
    z = 0.0
    z = x * y
    return z

d_side_effect = fwd_diff(side_effect)
