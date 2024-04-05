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
import unittest

epsilon = 1e-4

class Homework1Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_identity(self):
        with open('loma_code/identity.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/identity')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 4.56)
        out = lib.d_identity(x)
        assert abs(out.val - 1.23) < epsilon and abs(out.dval - 4.56) < epsilon

    def test_constant(self):
        with open('loma_code/constant.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/constant')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 4.56)
        out = lib.d_constant(x)
        assert abs(out.val - 2.0) < epsilon and abs(out.dval - 0.0) < epsilon

    def test_plus(self):
        with open('loma_code/plus.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/plus')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.5)
        y = _dfloat(6.0, 1.5)
        out_plus = lib.d_plus(x, y)
        assert abs(out_plus.val - (x.val + y.val)) < epsilon and \
               abs(out_plus.dval - (x.dval + y.dval)) < epsilon

    def test_subtract(self):
        with open('loma_code/subtract.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/subtract')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.5)
        y = _dfloat(6.0, 1.5)
        out_sub = lib.d_subtract(x, y)
        assert abs(out_sub.val - (x.val - y.val)) < epsilon and \
               abs(out_sub.dval - (x.dval - y.dval)) < epsilon

    def test_multiply(self):
        with open('loma_code/multiply.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/multiply')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.5)
        y = _dfloat(6.0, 1.5)
        out_mul = lib.d_multiply(x, y)
        assert abs(out_mul.val - x.val * y.val) < epsilon and \
               abs(out_mul.dval - (x.dval * y.val + x.val * y.dval)) < epsilon

    def test_divide(self):
        with open('loma_code/divide.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/divide')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.5)
        y = _dfloat(6.0, 1.5)
        out_div = lib.d_divide(x, y)
        assert abs(out_div.val - (x.val/y.val)) < epsilon and \
               abs(out_div.dval - ((x.dval * y.val - x.val * y.dval)/(y.val * y.val))) < epsilon

    def test_declare(self):
        with open('loma_code/declare.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/declare')
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

    def test_assign(self):
        with open('loma_code/assign.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign')
        _dfloat = structs['_dfloat']
        x = _dfloat(-3.0, -1.0)
        y = _dfloat(5.0, 3.0)
        out = lib.d_assign(x, y)

        assert abs(out.val - (-3.0 + 5.0)) < epsilon and \
            abs(out.dval - (-1.0 + 3.0)) < epsilon

    def test_side_effect(self):
        with open('loma_code/side_effect.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/side_effect')
        _dfloat = structs['_dfloat']
        x = _dfloat(-3.5, -1.5)
        y = _dfloat(7.0, 2.0)
        out = lib.d_side_effect(x, y)

        assert abs(out.val - (x.val * y.val)) < epsilon and \
            abs(out.dval - (x.dval * y.val + x.val * y.dval)) < epsilon

    def test_call_sin(self):
        with open('loma_code/call_sin.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_sin')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0.3)
        out = lib.d_call_sin(x)

        assert abs(out.val - math.sin(x.val)) < epsilon and \
            abs(out.dval - x.dval * math.cos(x.val)) < epsilon

    def test_call_cos(self):
        with open('loma_code/call_cos.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_cos')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0.3)
        out = lib.d_call_cos(x)

        assert abs(out.val - math.cos(x.val)) < epsilon and \
            abs(out.dval + x.dval * math.sin(x.val)) < epsilon

    def test_call_sqrt(self):
        with open('loma_code/call_sqrt.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_sqrt')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0.3)
        out = lib.d_call_sqrt(x)

        assert abs(out.val - math.sqrt(x.val)) < epsilon and \
            abs(out.dval - (0.5 * x.dval / math.sqrt(x.val))) < epsilon

    def test_call_pow(self):
        with open('loma_code/call_pow.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_pow')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0.3)
        y = _dfloat(0.7, 0.4)
        out = lib.d_call_pow(x, y)

        assert abs(out.val - math.pow(x.val, y.val)) < epsilon and \
            abs(out.dval - (x.dval * y.val * math.pow(x.val, y.val - 1) + \
                            y.dval * math.pow(x.val, y.val) * math.log(x.val))) < epsilon

    def test_call_exp(self):
        with open('loma_code/call_exp.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_exp')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0.3)
        out = lib.d_call_exp(x)

        assert abs(out.val - math.exp(x.val)) < epsilon and \
            abs(out.dval - x.dval * math.exp(x.val)) < epsilon

    def test_call_log(self):
        with open('loma_code/call_log.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_log')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0.3)
        out = lib.d_call_log(x)

        assert abs(out.val - math.log(x.val)) < epsilon and \
            abs(out.dval - x.dval / x.val) < epsilon

    def test_call(self):
        with open('loma_code/call.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call')
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

    def test_int_input(self):
        with open('loma_code/int_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_input')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 4.56)
        y = 3
        out = lib.d_int_input(x, y)
        assert abs(out.val - (5 * x.val + y - 1)) < epsilon and \
            abs(out.dval - 5 * x.dval) < epsilon

    def test_int_output(self):
        with open('loma_code/int_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_output')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 4.56)
        y = 3
        out = lib.d_int_output(x, y)
        assert abs(out - int(5 * x.val + y - 1)) < epsilon

    def test_array_output(self):
        with open('loma_code/array_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_output')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.8)
        py_y = [_dfloat(0.0, 0.0), _dfloat(0.0, 0.0)]
        y = (_dfloat * len(py_y))(*py_y)
        lib.d_array_output(x, y)
        assert abs(y[0].val - x.val * x.val) < epsilon and \
            abs(y[0].dval - 2 * x.val * x.dval) < epsilon and \
            abs(y[1].val - x.val * x.val * x.val) < epsilon and \
            abs(y[1].dval - 3 * x.val * x.val * x.dval) < epsilon

    def test_array_input(self):
        with open('loma_code/array_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_input')
        _dfloat = structs['_dfloat']
        py_x = [_dfloat(0.7, 0.8), _dfloat(0.3, 0.5)]
        x = (_dfloat * len(py_x))(*py_x)
        out = lib.d_array_input(x)
        assert abs(out.val - (0.7 + 0.3)) < epsilon and \
            abs(out.dval - (0.8 + 0.5)) < epsilon

    def test_int_array_input(self):
        with open('loma_code/int_array_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_array_input')
        _dfloat = structs['_dfloat']
        py_x = [_dfloat(0.7, 0.8), _dfloat(0.3, 0.5)]
        x = (_dfloat * len(py_x))(*py_x)
        py_y = [5]
        y = (ctypes.c_int * len(py_y))(*py_y)
        out = lib.d_int_array_input(x, y)
        assert abs(out.val - (0.7 + 0.3 + 5)) < epsilon and \
            abs(out.dval - (0.8 + 0.5)) < epsilon

    def test_array_input_indexing(self):
        with open('loma_code/array_input_indexing.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_input_indexing')
        _dfloat = structs['_dfloat']
        py_x = [_dfloat(0.1, 0.9),
                _dfloat(0.2, 0.8),
                _dfloat(0.3, 0.7),
                _dfloat(0.4, 0.6),
                _dfloat(0.5, 0.5),
                _dfloat(0.6, 0.4),
                _dfloat(0.7, 0.3)]
        x = (_dfloat * len(py_x))(*py_x)
        i = 1
        j = _dfloat(3.5, 0.5)
        out = lib.d_array_input_indexing(x, i, j)
        assert abs(out.val - (x[1].val + x[3].val + x[2].val + x[6].val)) < epsilon and \
            abs(out.dval - (x[1].dval + x[3].dval + x[2].dval + x[6].dval)) < epsilon

    def test_array_output_indexing(self):
        with open('loma_code/array_output_indexing.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_output_indexing')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.3, 0.4)
        i = 1
        j = _dfloat(3.5, 0.5)
        py_y = [_dfloat(0, 0)] * 7
        y = (_dfloat * len(py_y))(*py_y)
        lib.d_array_output_indexing(x, i, j, y)
        assert abs(y[0].val - 0) < epsilon and \
            abs(y[0].dval - 0) < epsilon
        assert abs(y[1].val - x.val) < epsilon and \
            abs(y[1].dval - x.dval) < epsilon
        assert abs(y[2].val - 3 * x.val) < epsilon and \
            abs(y[2].dval - 3 * x.dval) < epsilon
        assert abs(y[3].val - 2 * x.val) < epsilon and \
            abs(y[3].dval - 2 * x.dval) < epsilon
        assert abs(y[4].val - 0) < epsilon and \
            abs(y[4].dval - 0) < epsilon
        assert abs(y[5].val - 0) < epsilon and \
            abs(y[5].dval - 0) < epsilon
        assert abs(y[6].val - 4 * x.val) < epsilon and \
            abs(y[6].dval - 4 * x.dval) < epsilon

    def test_multiple_outputs(self):
        with open('loma_code/multiple_outputs.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/multiple_outputs')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.8)
        py_y = [_dfloat(0.0, 0.0), _dfloat(0.0, 0.0)]
        y = (_dfloat * len(py_y))(*py_y)
        z = _dfloat(0.5, -0.3)
        lib.d_multiple_outputs(x, y, ctypes.pointer(z))
        assert abs(y[0].val - x.val * x.val) < epsilon and \
            abs(y[0].dval - 2 * x.val * x.dval) < epsilon and \
            abs(y[1].val - x.val * x.val * x.val) < epsilon and \
            abs(y[1].dval - 3 * x.val * x.val * x.dval) < epsilon and \
            abs(z.val - y[0].val * y[1].val) < epsilon and \
            abs(z.dval - (y[0].val * y[1].dval + y[0].dval * y[1].val)) < epsilon

    def test_struct_input(self):
        with open('loma_code/struct_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_input')
        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        f = _dFoo(_dfloat(1.23, 4.56), 3)
        out = lib.d_struct_input(f)
        assert abs(out.val - (5 * f.x.val + f.y - 1)) < epsilon and \
            abs(out.dval - 5 * f.x.dval) < epsilon

    def test_nested_struct_input(self):
        with open('loma_code/nested_struct_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_struct_input')
        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        _dBar = structs['_dBar']
        f = _dFoo(_dfloat(1.23, 4.56), _dBar(3, _dfloat(1.23, 4.56)))
        out = lib.d_nested_struct_input(f)
        assert abs(out.val - (f.x.val + f.y.z + f.y.w.val + 5) * 3) < epsilon and \
            abs(out.dval - (f.x.dval + f.y.w.dval) * 3) < epsilon

    def test_struct_output(self):
        with open('loma_code/struct_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_output')

        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 4.56)
        y = 3
        out = lib.d_struct_output(x, y)
        assert abs(out.a.val - (x.val + y * x.val)) < epsilon and \
            abs(out.b - int(y - x.val)) < epsilon and \
            abs(out.a.dval - (x.dval + y * x.dval)) < epsilon

    def test_struct_declare(self):
        with open('loma_code/struct_declare.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_declare')

        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        f = _dFoo(a=_dfloat(1.23,4.56), b=3)
        out = lib.d_struct_declare(f)
        assert abs(out.a.val - f.a.val * 2) < epsilon and \
            out.b == f.b and \
            abs(out.a.dval - 2 * f.a.dval) < epsilon

    def test_struct_assign(self):
        with open('loma_code/struct_assign.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_assign')

        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        f = _dFoo(a=_dfloat(1.23,4.56), b=3)
        out = lib.d_struct_assign(f)
        assert abs(out.a.val - f.a.val * 2) < epsilon and \
            out.b == f.b and \
            abs(out.a.dval - 2 * f.a.dval) < epsilon

    def test_nested_struct_output(self):
        with open('loma_code/nested_struct_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_struct_output')

        _dfloat = structs['_dfloat']
        _dBar = structs['_dBar']
        a = _dfloat(1.23, 4.56)
        bar = _dBar()
        f = lib.d_nested_struct_output(a, ctypes.pointer(bar))
        assert abs(f.x.val - 2 * a.val) < epsilon and \
            f.y.z == 5 and \
            abs(f.y.w.val - f.x.val) < epsilon and \
            bar.z == 3 and \
            abs(bar.w.val - (bar.z * a.val)) < epsilon and \
            abs(f.x.dval - 2 * a.dval) < epsilon and \
            abs(f.y.w.dval - f.x.dval) < epsilon and \
            abs(bar.w.dval - (bar.z * a.dval)) < epsilon

    def test_array_in_struct(self):
        with open('loma_code/array_in_struct.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_in_struct')
        _dfloat = structs['_dfloat']
        int_arr = ctypes.c_int(3)
        float_arr = _dfloat(5.0, 7.0)
        _dFoo = structs['_dFoo']
        f = _dFoo(int_arr=ctypes.pointer(int_arr), float_arr=ctypes.pointer(float_arr))
        out = lib.d_array_in_struct(f)
        assert out.val - (int_arr.value + float_arr.val) < epsilon and \
            out.dval - float_arr.dval < epsilon

    def test_struct_in_array(self):
        with open('loma_code/struct_in_array.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_in_array')
        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']

        x = 3
        y = _dfloat(5.0, 7.0)
        in_f = _dFoo(x, y)
        out_f = _dFoo()
        lib.d_struct_in_array(ctypes.pointer(in_f), ctypes.pointer(out_f))
        assert out_f.x - int(x * y.val) < epsilon and \
            out_f.y.val - (x + y.val) < epsilon and \
            out_f.y.dval - y.dval < epsilon

    def test_poly(self):
        with open('loma_code/poly.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/poly')
        x = 0.6
        out = lib.d_poly_dx(x)
        # poly is 3x^4 + 5x^2 + 10
        # the derivative is 12 x^3 + 10 x
        assert out - (12 * x * x * x + 10 * x) < epsilon

if __name__ == '__main__':
    unittest.main()

