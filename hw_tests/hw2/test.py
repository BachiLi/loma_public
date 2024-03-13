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

class Homework2Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_identity(self):
        with open('loma_code/identity.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/identity.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        lib.d_identity(ctypes.byref(x), 4.56)
        assert abs(x.dval - 4.56) < epsilon

    def test_constant(self):
        with open('loma_code/constant.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/constant.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        lib.d_constant(ctypes.byref(x), 4.56)
        assert abs(x.dval - 0) < epsilon

    def test_binary_ops(self):
        with open('loma_code/binary_ops.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/binary_ops.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.0)
        y = _dfloat(6.0, 0.0)
        dout = 3.0
        lib.d_plus(ctypes.byref(x), ctypes.byref(y), dout)
        assert abs(x.dval - dout) < epsilon and \
               abs(y.dval - dout) < epsilon
        x = _dfloat(5.0, 0.0)
        y = _dfloat(6.0, 0.0)
        dout = 3.0
        lib.d_subtract(ctypes.byref(x), ctypes.byref(y), dout)
        assert abs(x.dval - dout) < epsilon and \
               abs(y.dval + dout) < epsilon
        x = _dfloat(5.0, 0.0)
        y = _dfloat(6.0, 0.0)
        dout = 3.0
        lib.d_multiply(ctypes.byref(x), ctypes.byref(y), dout)
        assert abs(x.dval - dout * y.val) < epsilon and \
               abs(y.dval - dout * x.val) < epsilon
        x = _dfloat(5.0, 0.0)
        y = _dfloat(6.0, 0.0)
        dout = 3.0
        lib.d_divide(ctypes.byref(x), ctypes.byref(y), dout)
        assert abs(x.dval - dout / y.val) < epsilon and \
               abs(y.dval + (dout * x.val) / (y.val * y.val)) < epsilon

    def test_square(self):
        with open('loma_code/square.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/square.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.0)
        dout = 3.0
        lib.d_square(ctypes.byref(x), dout)
        assert abs(x.dval - 2 * dout * x.val) < epsilon

    def test_declare(self):
        with open('loma_code/declare.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/declare.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(5.0, 0.0)
        y = _dfloat(6.0, 0.0)
        dout = 3.0
        lib.d_declare(ctypes.byref(x), ctypes.byref(y), dout)

        # simulate the reverse-diff program
        z0_val = x.val + y.val
        z1_val = z0_val + 5.0
        z2_val = z1_val * z0_val
        z3_val = z2_val / z1_val
        z4_val = z3_val - x.val

        z4_dval = dout
        # z4_val = z3_val - x.val
        z3_dval = dout
        x_dval = -dout
        # z3_val = z2_val / z1_val
        z2_dval = z3_dval / z1_val
        z1_dval = -z3_dval * z2_val / (z1_val * z1_val)
        # z2_val = z1_val * z0_val
        z1_dval += z2_dval * z0_val
        z0_dval = z2_dval * z1_val
        # z1_val = z0_val + 5.0
        z0_dval += z1_dval
        # z0_val = x.val + y.val
        x_dval += z0_dval
        y_dval = z0_dval

        assert abs(x.dval - x_dval) < epsilon and \
               abs(y.dval - y_dval) < epsilon

    def test_assign1(self):
        with open('loma_code/assign1.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign1.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(-3.0, 0.0)
        y = _dfloat(5.0, 0.0)
        dout = 3.0
        lib.d_assign1(ctypes.byref(x), ctypes.byref(y), dout)

        assert abs(x.dval - 3 * dout) < epsilon and \
            abs(y.dval - 5 * dout) < epsilon

    def test_assign2(self):
        with open('loma_code/assign2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign2.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(2.0, 0.0)
        y = _dfloat(-6.0, 0.0)
        dout = 3.5
        lib.d_assign2(ctypes.byref(x), ctypes.byref(y), dout)

        assert abs(x.dval - (2.5 + y.val) * dout) < epsilon and \
            abs(y.dval - (-3.0 + x.val) * dout) < epsilon

    def test_assign3(self):
        with open('loma_code/assign3.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign3.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(2.0, 0.0)
        y = _dfloat(-6.0, 0.0)
        dout = 3.5
        lib.d_assign3(x, y, dout)

        assert abs(x.dval - y.val * dout) < epsilon and \
            abs(y.dval - x.val * dout) < epsilon

    def test_assign4(self):
        with open('loma_code/assign4.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign4.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(2.0, 0.0)
        y = _dfloat(-6.0, 0.0)
        dout = 3.5
        lib.d_assign4(x, y, dout)

        # z1 = 2.5 * x - 3.0 * y
        # z2 = z1 * z1 + z1 * x * y + z1
        z1 = 2.5 * x.val - 3.0 * y.val
        z2 = z1 * z1 + z1 * x.val * y.val + z1

        dz2 = dout
        dz1 = 2 * z1 * dz2 + x.val * y.val * dz2 + dz2
        dx = dz2 * z1 * y.val
        dy = dz2 * z1 * x.val
        dx += dz1 * 2.5
        dy -= dz1 * 3.0

        assert abs(x.dval - dx) < epsilon and \
            abs(y.dval - dy) < epsilon

    def test_assign5(self):
        with open('loma_code/assign5.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign5.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(-3.0, 0.0)
        y = _dfloat(5.0, 0.0)
        dout = 3.0
        lib.d_assign5(x, y, dout)

        z0 = x.val * y.val
        w0 = z0
        z1 = x.val + y.val
        w1 = w0 + z1 * z1
        z2 = 2 * x.val
        z3 = z2 + 1.0
        z4 = 3.0 * z3 * z3 + w1

        dz4 = dout
        dz3 = dz4 * 6.0 * z3
        dw1 = dz4
        dz2 = dz3
        dx = dz2 * 2
        dw0 = dw1
        dz1 = dw1 * z1 * 2
        dx += dz1
        dy = dz1
        dz0 = dw0
        dx += dz0 * y.val
        dy += dz0 * x.val

        assert abs(x.dval - dx) < epsilon and \
            abs(y.dval - dy) < epsilon

    def test_assign_args(self):
        with open('loma_code/assign_args.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign_args.so')
        _dfloat = structs['_dfloat']
        w = _dfloat(-1.3, 0.0)
        x = _dfloat(-3.0, 0.0)
        y = _dfloat(5.0, 0.0)
        z = _dfloat(3.0, 0.0)
        dout = 2.7
        lib.d_assign_args(w, x, y, z, dout)

        w1 = 5.0
        x1 = w1 + x.val + y.val + z.val
        y1 = 6.0
        z1 = x1 * x1

        dz1 = dout
        dx1 = dz1 * 2 * x1
        dw1 = dx1
        dx = dx1
        dy = dx1
        dz = dx1
        dw = 0.0

        assert abs(w.dval - dw) < epsilon and \
            abs(x.dval - dx) < epsilon and \
            abs(y.dval - dy) < epsilon and \
            abs(z.dval - dz) < epsilon

    def test_refs_out1(self):
        with open('loma_code/refs_out1.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/refs_out1.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.0)
        y = _dfloat(0.0, 0.1)
        lib.d_refs_out1(ctypes.byref(x), ctypes.byref(y))

        assert abs(x.dval - 0.1 * 2 * x.val) < epsilon and \
            abs(y.dval - 0) < epsilon

    def test_refs_out2(self):
        with open('loma_code/refs_out2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/refs_out2.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.0)
        y = _dfloat(0.0, 0.1)
        lib.d_refs_out2(ctypes.byref(x), ctypes.byref(y))

        assert abs(x.dval - 0.1 * 3 * x.val * x.val) < epsilon and \
            abs(y.dval - 0) < epsilon

    def test_refs_out3(self):
        with open('loma_code/refs_out3.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/refs_out3.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.0)
        y = _dfloat(0.0, 0.1)
        z = _dfloat(0.0, 0.2)
        lib.d_refs_out3(ctypes.byref(x), ctypes.byref(y), ctypes.byref(z))

        # y = x * x
        # z = 2 * y
        # y = x + z
        dy = 0.1
        dz = 0.2

        dx = dy
        dz += dy
        dy = 2 * dz
        dx += dy * 3 * x.val * x.val

        assert abs(x.dval - dx) < epsilon and \
            abs(y.dval - 0) < epsilon and \
            abs(z.dval - 0) < epsilon

    def test_refs_inout(self):
        with open('loma_code/refs_inout.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/refs_inout.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.0)
        y = _dfloat(0.5, 0.1)
        z = _dfloat(0.0, 0.2)
        lib.d_refs_inout(ctypes.byref(x), ctypes.byref(y), ctypes.byref(z))

        # y1 = y * 5 - x * x
        # z = 2 * y1
        # y2 = x + z
        dy2 = 0.1
        dz = 0.2

        dx = dy2
        dz += dy2
        dy1 = 2 * dz
        dy = dy1 * 5
        dx -= dy1 * 2 * x.val

        assert abs(x.dval - dx) < epsilon and \
            abs(y.dval - dy) < epsilon and \
            abs(z.dval - 0) < epsilon

    def test_call_sin(self):
        with open('loma_code/call_sin.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_sin.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        dout = -0.3
        lib.d_call_sin(x, dout)

        assert abs(x.dval - dout * math.cos(x.val)) < epsilon

    def test_call_cos(self):
        with open('loma_code/call_cos.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_cos.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        dout = -0.3
        lib.d_call_cos(x, dout)

        assert abs(x.dval + dout * math.sin(x.val)) < epsilon

    def test_call_sqrt(self):
        with open('loma_code/call_sqrt.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_sqrt.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        dout = -0.3
        lib.d_call_sqrt(x, dout)

        assert abs(x.dval - (0.5 * dout / math.sqrt(x.val))) < epsilon

    def test_call_pow(self):
        with open('loma_code/call_pow.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_pow.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        y = _dfloat(0.7, 0)
        dout = -0.3
        lib.d_call_pow(x, y, dout)

        assert abs(x.dval - dout * y.val * math.pow(x.val, y.val - 1)) < epsilon and \
            abs(y.dval - dout * math.pow(x.val, y.val) * math.log(x.val)) < epsilon

    def test_call_exp(self):
        with open('loma_code/call_exp.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_exp.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        dout = -0.3
        lib.d_call_exp(x, dout)

        assert abs(x.dval - dout * math.exp(x.val)) < epsilon

    def test_call_log(self):
        with open('loma_code/call_log.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_log.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        dout = -0.3
        lib.d_call_log(x, dout)

        assert abs(x.dval - dout / x.val) < epsilon

    def test_call(self):
        with open('loma_code/call.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.5, 0)
        y = _dfloat(0.7, 0)
        dout = -0.3
        lib.d_call(x, y, dout)

        z0 = math.sin(x.val)
        z1 = math.cos(z0) + 1.0
        z2 = math.sqrt(z1) - y.val * y.val
        z3 = math.pow(z2, z1)
        z4 = math.exp(z3)
        z5 = math.log(z3 + z4)

        dz5 = dout
        dz3 = dout / (z3 + z4)
        dz4 = dout / (z3 + z4)
        dz3 += dz4 * z4
        dz2 = dz3 * z1 * math.pow(z2, z1 - 1)
        dz1 = dz3 * math.pow(z2, z1) * math.log(z2)
        dz1 += (0.5) * (dz2 / math.sqrt(z1))
        dy = -dz2 * 2 * y.val
        dz0 = -dz1 * math.sin(z0)
        dx = dz0 * math.cos(x.val)

        assert abs(x.dval - dx) < epsilon and \
            abs(y.dval - dy) < epsilon

    def test_int_input(self):
        with open('loma_code/int_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_input.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        y = ctypes.c_int(3)
        dout = 4.56
        lib.d_int_input(ctypes.byref(x), ctypes.byref(y), dout)
        assert abs(x.dval - dout * 5) < epsilon

    def test_int_output(self):
        with open('loma_code/int_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_output.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        y = ctypes.c_int(3)
        lib.d_int_output(ctypes.byref(x), ctypes.byref(y), 1)
        assert abs(x.dval - 0) < epsilon

    def test_int_assign(self):
        with open('loma_code/int_assign.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_assign.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        y = ctypes.c_int(3)
        dout = 0.3
        lib.d_int_assign(ctypes.byref(x), ctypes.byref(y), dout)
        # z0 = y
        # w = z0 * x
        # z1 = 6
        # return w * z1 * x + y - 1
        # -> y * x * 6 * x
        assert abs(x.dval - dout * (2 * 6 * 3 * x.val)) < epsilon

    def test_multivariate(self):
        with open('loma_code/multivariate.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/poly.so')
        x = ctypes.c_float(0.6)
        y = ctypes.c_float(0.7)
        dx = ctypes.c_float(0)
        dy = ctypes.c_float(0)
        lib.multivariate_grad(x, y, ctypes.byref(dx), ctypes.byref(dy))
        # out = 3 * x * cos (y) + y * y
        # dx = 3 * cos(y)
        # dy = - 3 * x * sin (y) + 2 * y
        assert abs(dx.value - 3 * math.cos(y.value)) < epsilon and \
            abs(dy.value - (-3 * x.value * math.sin(y.value) + 2 * y.value)) < epsilon

class Homework2Bonus(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_array_output(self):
        with open('loma_code/array_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_output.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.7, 0.0)
        py_y = [_dfloat(0.0, 0.3), _dfloat(0.0, 0.5)]
        y = (_dfloat * len(py_y))(*py_y)
        lib.d_array_output(x, y)
        assert abs(x.dval - (0.3 * 2 * x.val + 0.5 * 3 * x.val * x.val)) < epsilon

    def test_array_input(self):
        with open('loma_code/array_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_input.so')
        _dfloat = structs['_dfloat']
        py_x = [_dfloat(0.7, 0.0), _dfloat(0.3, 0.0)]
        x = (_dfloat * len(py_x))(*py_x)
        dout = -0.27
        lib.d_array_input(x, dout)
        assert abs(x[0].dval - 2 * dout) < epsilon and \
            abs(x[1].dval - 6 * x[1].val * dout) < epsilon

    def test_int_array_input(self):
        with open('loma_code/int_array_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_array_input.so')
        _dfloat = structs['_dfloat']
        py_x = [_dfloat(0.7, 0.0), _dfloat(0.3, 0.0)]
        x = (_dfloat * len(py_x))(*py_x)
        py_y = [5]
        y = (ctypes.c_int * len(py_y))(*py_y)
        dout = 0.5
        lib.d_int_array_input(x, y, dout)
        assert abs(x[0].dval - dout) < epsilon and \
            abs(x[1].dval - dout) < epsilon

    def test_array_input_indexing(self):
        with open('loma_code/array_input_indexing.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_input_indexing.so')
        _dfloat = structs['_dfloat']
        py_x = [_dfloat(0.1, 0.0),
                _dfloat(0.2, 0.0),
                _dfloat(0.3, 0.0),
                _dfloat(0.4, 0.0),
                _dfloat(0.5, 0.0),
                _dfloat(0.6, 0.0),
                _dfloat(0.7, 0.0)]
        x = (_dfloat * len(py_x))(*py_x)
        i = ctypes.c_int(1)
        j = _dfloat(3.5, 0.0)
        dout = -0.5
        lib.d_array_input_indexing(x, ctypes.byref(i), ctypes.byref(j), dout)
        assert abs(x[1].dval - dout * x[3].val) < epsilon and \
            abs(x[3].dval - dout * x[1].val) < epsilon and \
            abs(x[2].dval - dout * x[6].val) < epsilon and \
            abs(x[6].dval - dout * x[2].val) < epsilon and \
            abs(x[4].dval - dout * x[5].val) < epsilon and \
            abs(x[5].dval - dout * x[4].val) < epsilon

    def test_array_output_indexing(self):
        with open('loma_code/array_output_indexing.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_output_indexing.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.3, 0.0)
        i = ctypes.c_int(1)
        j = _dfloat(3.5, 0.0)
        py_y = [_dfloat(0, 0.1),
                _dfloat(0, 0.2),
                _dfloat(0, 0.3),
                _dfloat(0, 0.4),
                _dfloat(0, 0.5),
                _dfloat(0, 0.6),
                _dfloat(0, 0.7)]
        y = (_dfloat * len(py_y))(*py_y)
        lib.d_array_output_indexing(ctypes.byref(x), ctypes.byref(i), ctypes.byref(j), y)
        # y[1] = x
        # y[3] = 2 * x
        # y[2] = 3 * x
        # y[6] = 4 * x
        assert abs(x.dval - (0.2 + 0.4 * 2 + 0.3 * 3 + 0.7 * 4)) < epsilon and \
            abs(j.dval - 0) < epsilon

    def test_array_in_out(self):
        with open('loma_code/array_in_out.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_in_out.so')
        _dfloat = structs['_dfloat']
        i = ctypes.c_int(1)
        j = _dfloat(3.5, 0.0)
        py_y = [_dfloat(0.7, 0.1),
                _dfloat(0.6, 0.2),
                _dfloat(0.5, 0.3),
                _dfloat(0.4, 0.4),
                _dfloat(0.3, 0.5),
                _dfloat(0.2, 0.6),
                _dfloat(0.1, 0.7)]
        y = (_dfloat * len(py_y))(*py_y)
        lib.d_array_in_out(ctypes.byref(i), ctypes.byref(j), y)
        # y[1] = y[3] * y[6]
        assert abs(y[3].dval - (0.4 + 0.2 * y[6].val)) < epsilon and \
            abs(y[6].dval - (0.7 + 0.2 * y[3].val)) < epsilon

    def test_sum_nested_array(self):
        with open('loma_code/sum_nested_array.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/sum_nested_array.so')
        _dfloat = structs['_dfloat']
        pointer_arr = (ctypes.POINTER(_dfloat) * 3)()
        arr0 = (_dfloat * 3)(_dfloat(0.1,0.0),_dfloat(0.2,0.0),_dfloat(0.3,0.0))
        pointer_arr[0] = ctypes.cast(ctypes.pointer(arr0), ctypes.POINTER(_dfloat))
        arr1 = (_dfloat * 2)(_dfloat(0.4,0.0),_dfloat(0.5,0.0))
        pointer_arr[1] = ctypes.cast(ctypes.pointer(arr1), ctypes.POINTER(_dfloat))
        arr2 = (_dfloat * 1)(_dfloat(0.6,0.0))
        pointer_arr[2] = ctypes.cast(ctypes.pointer(arr2), ctypes.POINTER(_dfloat))
        dout = 0.3
        lib.d_sum_nested_array(pointer_arr, dout)
        assert abs(pointer_arr[0][0].dval - 2 * dout * pointer_arr[0][0].val) < epsilon and \
               abs(pointer_arr[0][1].dval - 2 * dout * pointer_arr[0][1].val) < epsilon and \
               abs(pointer_arr[0][2].dval - 2 * dout * pointer_arr[0][2].val) < epsilon and \
               abs(pointer_arr[1][0].dval - 2 * dout * pointer_arr[1][0].val) < epsilon and \
               abs(pointer_arr[1][1].dval - 2 * dout * pointer_arr[1][1].val) < epsilon and \
               abs(pointer_arr[2][0].dval - 2 * dout * pointer_arr[2][0].val) < epsilon

    def test_struct_input(self):
        with open('loma_code/struct_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_input.so')
        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        f = _dFoo(_dfloat(1.23, 0.0), 3, _dfloat(4.56, 0.0))
        dout = 0.3
        # out = 5 * foo.x + foo.y + foo.x * foo.z - 1
        lib.d_struct_input(f, dout)
        assert abs(f.x.dval - dout * (5 + f.z.val)) < epsilon and \
            abs(f.z.dval - dout * (f.x.val))

    def test_nested_struct_input(self):
        with open('loma_code/nested_struct_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_struct_input.so')
        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        _dBar = structs['_dBar']
        f = _dFoo(_dfloat(1.23, 0.0), _dBar(3, _dfloat(4.56, 0.0)))
        dout = 0.3
        lib.d_nested_struct_input(f, dout)
        # (foo.x + foo.y.z + foo.y.w + 5) * 3
        assert abs(f.x.dval - dout * 3) < epsilon and \
            abs(f.y.w.dval - dout * 3) < epsilon

    def test_struct_output(self):
        with open('loma_code/struct_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_output.so')

        _dfloat = structs['_dfloat']
        Foo = structs['Foo']
        x = _dfloat(1.23, 0.0)
        y = ctypes.c_int(3)
        dout = Foo(a=0.5,b=100)
        lib.d_struct_output(ctypes.byref(x), ctypes.byref(y), dout)
        # foo.a = x + y * x
        assert abs(x.dval - 0.5 * (1 + 3)) < epsilon

    def test_struct_declare(self):
        with open('loma_code/struct_declare.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_declare.so')

        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        Foo = structs['Foo']
        f = _dFoo(a=_dfloat(1.23,0.0), b=3)
        dout = Foo(a=0.3,b=100)
        lib.d_struct_declare(ctypes.byref(f), dout)
        assert abs(f.a.dval - dout.a * 2) < epsilon

    def test_struct_assign(self):
        with open('loma_code/struct_assign.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_assign.so')

        _dfloat = structs['_dfloat']
        _dFoo = structs['_dFoo']
        Foo = structs['Foo']
        f = _dFoo(a=_dfloat(1.23,0.0), b=3)
        dout = Foo(a=0.3,b=100)
        lib.d_struct_assign(ctypes.byref(f), dout)
        assert abs(f.a.dval - dout.a * 2) < epsilon

if __name__ == '__main__':
    unittest.main()
