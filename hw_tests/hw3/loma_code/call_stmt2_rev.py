def foo(x : In[float], y : Out[float]):
    y = x * x + x

def call_stmt2(x : In[float], y : Out[float]):
    foo(x, y)

rev_call_stmt2 = rev_diff(call_stmt2)
