import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import error

def declaration_float() -> float:
    x : float = 5
    return x

def declaration_int() -> int:
    x : int = 4
    return x

def test_declaration():
    lib = compiler.compile(declaration_float)
    assert(abs(lib.declaration_float() - 5) < 1e-6)
    lib = compiler.compile(declaration_int)
    assert(lib.declaration_int() == 4)

def binaryops() -> float:
    x : float = 5.0
    y : float = 6.0
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
    assert(abs(lib.binaryops() - 36.0 / 11.0) < 1e-6)

def args(x : float, y : int) -> int:
    z : int = x
    return z + y

def test_args():
    lib = compiler.compile(args)
    assert(lib.args(4.5, 3) == 7)

def mutation() -> float:
    a : float = 5.0
    a = 6.0
    return a

def test_mutation():
    lib = compiler.compile(mutation)
    assert(abs(lib.mutation() - 6) < 1e-6)


def duplicate_declare() -> float:
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

def undeclared_var() -> float:
    a : float = 5.0
    b = 6.0
    return a

def test_undeclared_var():
    try:
        lib = compiler.compile(undeclared_var)
    except error.UndeclaredVariable as e:
        assert(e.var == 'b')
        assert(e.lineno == 3)

if __name__ == '__main__':
    test_declaration()
    test_binary_ops()
    test_args()
    test_mutation()

    # test compile errors
    test_duplicate_declare()
    test_undeclared_var()
