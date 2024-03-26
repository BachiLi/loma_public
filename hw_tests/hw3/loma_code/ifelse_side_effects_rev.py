def ifelse_side_effects(x : In[float], y : In[float]) -> float:
    ret : float
    if y > 0.0:
        ret = 5.0 * x
        ret = sin(ret)
    else:
        ret = 2.0 * x
    return ret

rev_ifelse_side_effects = rev_diff(ifelse_side_effects)
