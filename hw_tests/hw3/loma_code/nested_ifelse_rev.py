def nested_ifelse(x : In[float], y : In[float]) -> float:
    ret : float
    if y > 0.0:
        ret = 5.0 * x
        if x > 0.0:
            ret = sin(ret)
        else:
            ret = cos(ret)
    else:
        ret = 2.0 * x
    return ret

rev_nested_ifelse = rev_diff(nested_ifelse)
