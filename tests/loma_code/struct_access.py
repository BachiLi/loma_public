class Foo:
    x : int
    y : float

def struct_access(f : In[Foo]) -> float:
    return f.x * f.y
