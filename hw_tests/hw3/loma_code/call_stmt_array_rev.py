def foo(x : In[Array[float]], y : Out[Array[float]]):
    y[0] = x[0] * x[0] + x[0]

def call_stmt_array(x : In[Array[float]], y : Out[Array[float]]):
    foo(x, y)

rev_call_stmt_array = rev_diff(call_stmt_array)
