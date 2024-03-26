def foo(x : In[float], y : In[float]) -> float:
    return x * y

def func_call(x : In[float], y : In[float]) -> float:
    z : float = foo(x + y, x * y)
    return 2 * z

rev_func_call = rev_diff(func_call)
