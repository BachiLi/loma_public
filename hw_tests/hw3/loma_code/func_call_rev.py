def foo(x : In[float], y : In[float]) -> float:
    return x * x * y + y * y

def func_call(x : In[float], y : In[float]) -> float:
    z : float = foo(x, y)
    return 2 * z

rev_func_call = rev_diff(func_call)
