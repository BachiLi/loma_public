import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import error

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

def duplicate_declare():
    x : float = 5
    x : float = 6
    return 0

def test_duplicate_declare():
    try:
        lib = compiler.compile(duplicate_declare)
    except error.DuplicateVariable as e:
        assert(e.var == 'x')
        assert(e.first_lineno == 2)
        assert(e.duplicate_lineno == 3)

def mutation():
    a : float = 5.0
    a = 6.0
    return a

def test_mutation():
    lib = compiler.compile(mutation)
    assert(abs(lib.mutation() - 6) < 1e-6)

if __name__ == '__main__':
    test_declaration()
    test_binary_ops()
    test_duplicate_declare()
    test_mutation()

