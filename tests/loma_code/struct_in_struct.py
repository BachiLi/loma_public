class Foo:
    x : int
    bar : Bar

class Bar:
    y : float
    z : int

def struct_in_struct(bar : In[Bar]) -> Foo:
    f : Foo
    f.x = 5
    f.bar = bar
    f.bar.z = 3
    return f
