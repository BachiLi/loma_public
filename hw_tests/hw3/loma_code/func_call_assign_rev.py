def foo(x : In[float], y : In[float]) -> float:
    return x * y

def func_call_assign(x : In[float], y : In[float]) -> float:
    z : float = foo(x, y)
    z = foo(z, y) # x * y * y
    z = foo(z, x) # x * x * y * y
    return 2 * z

rev_func_call_assign = rev_diff(func_call_assign)
