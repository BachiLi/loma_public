import compiler

def add(x : float, y : float):
    return x + y

lib = compiler.compile(add)
print(lib.add(float(5.0), float(6.0)))
