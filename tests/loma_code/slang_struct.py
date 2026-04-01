class Foo:
    a : float
    b : int

@simd
def slang_struct(x : In[Array[Foo]],
                 z : Out[Array[Foo]]):
    i : int = thread_id()
    z[i].a = x[i].a
    z[i].b = x[i].b
