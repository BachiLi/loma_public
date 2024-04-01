def foo(y : Out[int]) -> int:
    y = 10
    return 20

def call_not_in_call_stmt() -> int:
    y : int
    z : int = foo(y) # not legal, foo needs to be called in a CallStmt
    return z
