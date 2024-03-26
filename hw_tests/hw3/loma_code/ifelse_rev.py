def ifelse(x : In[float], y : In[float]) -> float:
    ret : float
    if y > 0.0:
        ret = 5.0 * x
    else:
        ret = 2.0 * x
    return ret

rev_ifelse = rev_diff(ifelse)
