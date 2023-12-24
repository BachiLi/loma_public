import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler

def add(x : float, y : float):
    return x + y

def test_binary_ops():
    lib = compiler.compile(add)
    assert(abs(lib.add(float(5.0), float(6.0)) - 11.0) < 1e-6)

def declaration():
    x : float = 5
    return x

def test_declaration():
    lib = compiler.compile(declaration)
    assert(abs(lib.declaration() - 5) < 1e-6)

if __name__ == '__main__':
    test_binary_ops()
    test_assignment()
