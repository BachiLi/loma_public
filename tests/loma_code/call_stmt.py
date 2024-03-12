def foo(x : Ref[int]):
    x = 5

def call_stmt() -> int:
    x : int
    foo(x)
    return x
