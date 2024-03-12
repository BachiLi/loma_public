def multivariate(x : float, y : float) -> float:
    return 3 * x * cos(y) + y * y

d_multivariate = rev_diff(multivariate)

def multivariate_grad(x : float, y : float, dx : Ref[float], dy : Ref[float]):
    dx_ : Diff[float]
    dx_.val = x
    dx_.dval = 0.0
    dy_ : Diff[float]
    dy_.val = y
    dy_.dval = 0.0

    d_multivariate(dx_, dy_, 1.0)
    dx = dx_.dval
    dy = dy_.dval
