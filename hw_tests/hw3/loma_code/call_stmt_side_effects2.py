def foo(x : In[float], y : Out[float]):
    y = x * x + x

def call_stmt_side_effects2(x : In[float], y : In[float]) -> float:
    y0 : float = 0.5 * y
    z : float = y0 * y0 * x
    foo(x, y0)
    return 2 * y0 + z

rev_call_stmt_side_effects2 = rev_diff(call_stmt_side_effects2)
