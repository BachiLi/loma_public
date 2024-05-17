def foo(x : In[Array[float]]) -> float:
    return x[0] * x[0] + x[0]

def call_array(x : In[Array[float]]) -> float:
    y : float
    y = foo(x)
    return y

rev_call_array = rev_diff(call_array)
