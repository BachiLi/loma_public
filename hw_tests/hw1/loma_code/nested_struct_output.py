class Foo:
    x : float
    y : Bar

class Bar:
    z : int
    w : float

def nested_struct_output(a : In[float], bar : Out[Array[Bar]]) -> Foo:
    f : Foo
    f.x = 2 * a
    f.y.z = 5
    f.y.w = f.x

    bar[0].z = 3
    bar[0].w = bar[0].z * a
    return f

d_nested_struct_output = fwd_diff(nested_struct_output)
