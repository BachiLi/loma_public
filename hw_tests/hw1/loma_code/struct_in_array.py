class Foo:
    x : int
    y : float

def struct_in_array(in_f : In[Array[Foo]], out_f : Out[Array[Foo]]):
    out_f[0].x = in_f[0].x * in_f[0].y
    out_f[0].y = in_f[0].x + in_f[0].y

d_struct_in_array = fwd_diff(struct_in_array)
