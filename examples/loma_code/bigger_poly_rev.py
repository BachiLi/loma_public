def bigger_poly(x : In[Array[float]]) -> float:
    term0 : float = 0.02 * x[0] * x[0] * x[1] * x[2] * x[4]
    term1 : float = -0.01 * x[1] * x[2] * x[3] * x[4] * x[4]
    term2 : float = 0.1 * x[0] * x[1] * x[4]
    term3 : float = 0.2 * x[2] * x[2] * x[3]
    term4 : float = -0.2 * x[1] * x[3] * x[3]
    term5 : float = 0.5 * x[0] * x[0]
    term6 : float = 0.6 * x[1] * x[1]
    term7 : float = 0.4 * x[2] * x[2]
    term8 : float = 0.5 * x[3] * x[3]
    term9 : float = 0.3 * x[4] * x[4]
    term10 : float = 0.1 * x[3]
    term11 : float = 0.2 * x[4]
    term12 : float = -0.1
    return term0 + term1 + term2 + term3 + \
        term4 + term5 + term6 + term7 + \
        term8 + term9 + term10 + term11 + \
        term12

rev_bigger_poly = rev_diff(bigger_poly)

def grad_bigger_poly(x : In[Array[float]], gx : Out[Array[float]]):
    rev_bigger_poly(x, gx, 1.0)
