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

epsilon = 1e-5

def test_identity():
    with open('loma_code/identity.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/identity.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(1.23, 4.56)
    out = lib.d_identity(x)
    assert abs(out.val - 1.23) < epsilon and abs(out.dval - 4.56) < epsilon

def test_constant():
    with open('loma_code/constant.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/constant.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(1.23, 4.56)
    out = lib.d_constant(x)
    assert abs(out.val - 2.0) < epsilon and abs(out.dval - 0.0) < epsilon

def test_binary_ops():
    with open('loma_code/binary_ops.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/binary_ops.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(5.0, 0.5)
    y = _dfloat(6.0, 1.5)
    out_plus = lib.d_plus(x, y)
    assert abs(out_plus.val - (x.val + y.val)) < epsilon and \
           abs(out_plus.dval - (x.dval + y.dval)) < epsilon
    out_sub = lib.d_subtract(x, y)
    assert abs(out_sub.val - (x.val - y.val)) < epsilon and \
           abs(out_sub.dval - (x.dval - y.dval)) < epsilon
    out_mul = lib.d_multiply(x, y)
    assert abs(out_mul.val - x.val * y.val) < epsilon and \
    	   abs(out_mul.dval - (x.dval * y.val + x.val * y.dval)) < epsilon
    out_div = lib.d_divide(x, y)
    assert abs(out_div.val - (x.val/y.val)) < epsilon and \
           abs(out_div.dval - ((x.dval * y.val - x.val * y.dval)/(y.val * y.val))) < epsilon

def test_declare():
    with open('loma_code/declare.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/declare.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(5.0, 0.5)
    y = _dfloat(6.0, 1.5)
    out = lib.d_declare(x, y)

    # simulate the forward-diff program
    z0_val = x.val + y.val
    z0_dval = x.dval + y.dval
    z1_val = z0_val + 5.0
    z1_dval = z0_dval + 0.0
    z2_val = z1_val * z0_val
    z2_dval = z1_dval * z0_val + z0_dval * z1_val

    assert abs(out.val - z2_val) < epsilon and \
           abs(out.dval - z2_dval) < epsilon

def test_assign():
    with open('loma_code/assign.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/assign.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(-3.0, -1.0)
    y = _dfloat(5.0, 3.0)
    out = lib.d_assign(x, y)

    assert abs(out.val - (-3.0 + 5.0)) < epsilon and \
           abs(out.dval - (-1.0 + 3.0)) < epsilon

def test_side_effect():
    with open('loma_code/side_effect.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/side_effect.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(-3.5, -1.5)
    y = _dfloat(7.0, 2.0)
    out = lib.d_side_effect(x, y)

    assert abs(out.val - (x.val * y.val)) < epsilon and \
           abs(out.dval - (x.dval * y.val + x.val * y.dval)) < epsilon

def test_call():
    with open('loma_code/call.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/call.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(1.5, 1.2)
    # z0 : float = sin(x)
    # z1 : float = cos(z0) + 1.0
    # z2 : float = sqrt(z1)
    # z3 : float = pow(z2, z1)
    # z4 : float = exp(z3)
    # z5 : float = log(z3 + z4)
    z0_val = math.sin(x.val)
    z0_dval = math.cos(x.val) * x.dval
    z1_val = math.cos(z0_val) + 1.0
    z1_dval = -math.sin(z0_val) * z0_dval
    z2_val = math.sqrt(z1_val)
    z2_dval = z1_dval / (2 * math.sqrt(z1_val))
    z3_val = math.pow(z2_val, z1_val)
    z3_dval = z2_dval * z1_val * math.pow(z2_val, z1_val - 1) \
            + z1_dval * math.pow(z2_val, z1_val) * math.log(z2_val)
    z4_val = math.exp(z3_val)
    z4_dval = math.exp(z3_val) * z3_dval
    z5_val = math.log(z3_val + z4_val)
    z5_dval = (z3_dval + z4_dval) / (z3_val + z4_val)

    out = lib.d_call(x)

    assert abs(out.val - z5_val) < epsilon and \
           abs(out.dval - z5_dval) < epsilon

def test_array_output():
    with open('loma_code/array_output.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/array_output.so')
    _dfloat = structs['_dfloat']
    x = _dfloat(0.7, 0.8)
    py_y = [_dfloat(0.0, 0.0), _dfloat(0.0, 0.0)]
    y = (_dfloat * len(py_y))(*py_y)
    lib.d_array_output(x, y)
    assert abs(y[0].val - x.val * x.val) < epsilon and \
           abs(y[0].dval - 2 * x.val * x.dval) < epsilon and \
           abs(y[1].val - x.val * x.val * x.val) < epsilon and \
           abs(y[1].dval - 3 * x.val * x.val * x.dval) < epsilon

def test_array_input():
    with open('loma_code/array_input.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/array_input.so')
    _dfloat = structs['_dfloat']
    py_x = [_dfloat(0.7, 0.8), _dfloat(0.3, 0.5)]
    x = (_dfloat * len(py_x))(*py_x)
    out = lib.d_array_input(x)
    assert abs(out.val - (0.7 + 0.3)) < epsilon and \
           abs(out.dval - (0.8 + 0.5)) < epsilon

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    test_identity()
    test_constant()
    test_binary_ops()
    test_declare()
    test_assign()
    test_side_effect()
    test_call()
    test_array_output()
    test_array_input()
