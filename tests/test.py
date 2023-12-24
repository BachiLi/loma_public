import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler

def declaration():
    x : float = 5
    return x

def test_declaration():
    lib = compiler.compile(declaration)
    assert(abs(lib.declaration() - 5) < 1e-6)

def binaryops(x : float, y : float):
    a : float = x + y
    b : float = a - x
    c : float = b * y
    d : float = c / a
    return d

def test_binary_ops():
    lib = compiler.compile(binaryops)
    # a = x + y = 5 + 6 = 11
    # b = a - x = 11 - 5 = 6
    # c = b * y = 6 * 6 = 36
    # d = c / a = 36 / 11
    assert(abs(lib.binaryops(float(5.0), float(6.0)) - 36.0 / 11.0) < 1e-6)

if __name__ == '__main__':
    test_declaration()
    test_binary_ops()
