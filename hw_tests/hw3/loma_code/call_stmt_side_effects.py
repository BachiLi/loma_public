def foo(x : In[float], y : Out[float]):
    y = x * x + x

def call_stmt_side_effects(x : In[float]) -> float:
    y : float = 10.0
    z : float = y * x
    foo(x, y)
    return 2.0 * y + z

rev_call_stmt_side_effects = rev_diff(call_stmt_side_effects)
