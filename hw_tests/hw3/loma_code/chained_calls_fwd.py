def f(x : In[float]) -> float:
    return x * x

def g(x : In[float]) -> float:
    return x + x

def h(x : In[float]) -> float:
    return sin(x)

def chained_calls(x : In[float]) -> float:
    return h(g(f(2 * x - x)))

fwd_chained_calls = fwd_diff(chained_calls)
