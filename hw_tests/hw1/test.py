import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent)
import compiler
import ctypes
import error
import math
import gpuctypes.opencl as cl
import cl_utils

def test_identity():
    with open('loma_code/identity.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/identity.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(123.0, 1.0)
    out = lib.d_identity(x)
    assert abs(out.val - 123.0) < 1e-6 and abs(out.dval - 1.0) < 1e-6

def test_binary_ops():
    with open('loma_code/binary_ops.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/binary_ops.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(5.0, 1.0)
    y = _dfloat(6.0, 1.0)
    out_plus = lib.d_plus(x, y)
    assert abs(out_plus.val - 11.0) < 1e-6 and abs(out_plus.dval - 2.0) < 1e-6
    out_sub = lib.d_subtract(x, y)
    assert abs(out_sub.val - (-1.0)) < 1e-6 and abs(out_sub.dval - 0.0) < 1e-6
    out_mul = lib.d_multiply(x, y)
    assert abs(out_mul.val - 30.0) < 1e-6 and abs(out_mul.dval - 11.0) < 1e-6
    out_div = lib.d_divide(x, y)
    assert abs(out_div.val - (5.0/6.0)) < 1e-6 and abs(out_div.dval - ((6.0 - 5.0) / (6.0 * 6.0))) < 1e-6

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    test_identity()
    test_binary_ops()
