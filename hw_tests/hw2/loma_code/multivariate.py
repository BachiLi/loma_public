def multivariate(x : In[float], y : In[float]) -> float:
    return 3 * x * cos(y) + y * y

d_multivariate = rev_diff(multivariate)

def multivariate_grad(x : In[float], y : In[float], dx : Out[float], dy : Out[float]):
    d_multivariate(x, dx, y, dy, 1.0)
