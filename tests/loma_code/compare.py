def compare(x : In[int], y : In[int],
            out : Out[Array[int]]):
    out[0] = x < y
    out[1] = x <= y
    out[2] = x > y
    out[3] = x >= y
    out[4] = x == y
    out[5] = x < y and x > y
    out[6] = x < y or x > y
