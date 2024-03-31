def foo(x : In[float], y : Out[float]):
    y = x * x + x

def call_stmt(x : In[float]) -> float:
    y : float
    foo(x, y)
    return 2 * y

fwd_call_stmt = fwd_diff(call_stmt)
