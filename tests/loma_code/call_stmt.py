def foo(x : Out[int]):
    x = 5

def call_stmt() -> int:
    x : int
    foo(x)
    return x
