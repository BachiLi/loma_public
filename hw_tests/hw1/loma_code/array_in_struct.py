class Foo:
    int_arr : Array[int]
    float_arr : Array[float]

def array_in_struct(f : In[Foo]) -> float:
    return f.int_arr[0] + f.float_arr[0]

d_array_in_struct = fwd_diff(array_in_struct)
