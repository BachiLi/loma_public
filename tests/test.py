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
    assert(lib.add(float(5.0), float(6.0)))

if __name__ == '__main__':
    test_binary_ops()