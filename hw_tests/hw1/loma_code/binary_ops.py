def plus(x : In[float], y : In[float]) -> float:
    return x + y

def subtract(x : In[float], y : In[float]) -> float:
    return x - y

def multiply(x : In[float], y : In[float]) -> float:
    return x * y

def divide(x : In[float], y : In[float]) -> float:
    return x / y

d_plus = fwd_diff(plus)
d_subtract = fwd_diff(subtract)
d_multiply = fwd_diff(multiply)
d_divide = fwd_diff(divide)
