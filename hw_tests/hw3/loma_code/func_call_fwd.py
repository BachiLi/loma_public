def foo(x : float, y : float) -> float:
    return x * x * y + y * y

def func_call(x : float, y : float) -> float:
    z : float = foo(x, y)
    return 2 * z

fwd_func_call = fwd_diff(func_call)
