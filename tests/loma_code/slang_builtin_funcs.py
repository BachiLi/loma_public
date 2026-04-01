@simd
def slang_builtin_funcs(x : In[Array[float]],
                        z : Out[Array[float]]):
    z0 : float = sin(x[thread_id()])
    z1 : float = cos(z0) + 1.0
    z2 : float = sqrt(z1)
    z3 : float = pow(z2, z1)
    z4 : float = exp(z3)
    z5 : float = log(z3 + z4)
    z[thread_id()] = z5
