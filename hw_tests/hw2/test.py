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
                                            output_filename = '_code/identity')
        _dx = ctypes.c_float(0.0)
        lib.d_identity(1.23, ctypes.byref(_dx), 4.56)
        assert abs(_dx.value - 4.56) < epsilon

    def test_constant(self):
        with open('loma_code/constant.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/constant')
        _dx = ctypes.c_float(0.0)
        lib.d_constant(1.23, ctypes.byref(_dx), 4.56)
        assert abs(_dx.value - 0) < epsilon

    def test_plus(self):
        with open('loma_code/plus.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/plus')
        x = 5.0
        _dx = ctypes.c_float(0)
        y = 6.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_plus(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        assert abs(_dx.value - dout) < epsilon and \
               abs(_dy.value - dout) < epsilon

    def test_subtract(self):
        with open('loma_code/subtract.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/subtract')
        x = 5.0
        _dx = ctypes.c_float(0)
        y = 6.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_subtract(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        assert abs(_dx.value - dout) < epsilon and \
               abs(_dy.value + dout) < epsilon

    def test_multiply(self):
        with open('loma_code/multiply.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/multiply')
        x = 5.0
        _dx = ctypes.c_float(0)
        y = 6.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_multiply(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        assert abs(_dx.value - dout * y) < epsilon and \
               abs(_dy.value - dout * x) < epsilon

    def test_divide(self):
        with open('loma_code/divide.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/divide')
        x = 5.0
        _dx = ctypes.c_float(0)
        y = 6.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_divide(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        assert abs(_dx.value - dout / y) < epsilon and \
               abs(_dy.value + (dout * x) / (y * y)) < epsilon

    def test_square(self):
        with open('loma_code/square.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/square')
        x = 5.0
        _dx = ctypes.c_float(0)
        dout = 3.0
        lib.d_square(x, ctypes.byref(_dx), dout)
        assert abs(_dx.value - 2 * dout * x) < epsilon

    def test_declare(self):
        with open('loma_code/declare.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/declare')
        x = 5.0
        _dx = ctypes.c_float(0)
        y = 6.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_declare(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        # simulate the reverse-diff program
        z0_val = x + y
        z1_val = z0_val + 5.0
        z2_val = z1_val * z0_val
        z3_val = z2_val / z1_val
        z4_val = z3_val - x

        z4_dval = dout
        # z4_val = z3_val - x
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
        # z0_val = x + y
        x_dval += z0_dval
        y_dval = z0_dval

        assert abs(_dx.value - x_dval) < epsilon and \
               abs(_dy.value - y_dval) < epsilon

    def test_assign1(self):
        with open('loma_code/assign1.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign1')
        x = -3.0
        _dx = ctypes.c_float(0)
        y = 5.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_assign1(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        assert abs(_dx.value - 3 * dout) < epsilon and \
            abs(_dy.value - 5 * dout) < epsilon

    def test_assign2(self):
        with open('loma_code/assign2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign2')
        x = 2.0
        _dx = ctypes.c_float(0)
        y = -6.0
        _dy = ctypes.c_float(0)
        dout = 3.5
        lib.d_assign2(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        assert abs(_dx.value - (2.5 + y) * dout) < epsilon and \
            abs(_dy.value - (-3.0 + x) * dout) < epsilon

    def test_assign3(self):
        with open('loma_code/assign3.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign3')
        x = 2.0
        _dx = ctypes.c_float(0)
        y = -6.0
        _dy = ctypes.c_float(0)
        dout = 3.5
        lib.d_assign3(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        assert abs(_dx.value - y * dout) < epsilon and \
            abs(_dy.value - x * dout) < epsilon

    def test_assign4(self):
        with open('loma_code/assign4.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign4')
        x = 2.0
        _dx = ctypes.c_float(0)
        y = -6.0
        _dy = ctypes.c_float(0)
        dout = 3.5
        lib.d_assign4(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        z1 = 2.5 * x - 3.0 * y
        z2 = z1 * z1 + z1 * x * y + z1

        dz2 = dout
        dz1 = 2 * z1 * dz2 + x * y * dz2 + dz2
        dx = dz2 * z1 * y
        dy = dz2 * z1 * x
        dx += dz1 * 2.5
        dy -= dz1 * 3.0

        assert abs(_dx.value - dx) < epsilon and \
            abs(_dy.value - dy) < epsilon

    def test_assign5(self):
        with open('loma_code/assign5.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign5')
        x = -3.0
        _dx = ctypes.c_float(0)
        y = 5.0
        _dy = ctypes.c_float(0)
        dout = 3.0
        lib.d_assign5(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        z0 = x * y
        w0 = z0
        z1 = x + y
        w1 = w0 + z1 * z1
        z2 = 2 * x
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
        dx += dz0 * y
        dy += dz0 * x

        assert abs(_dx.value - dx) < epsilon and \
            abs(_dy.value - dy) < epsilon

    def test_assign_args(self):
        with open('loma_code/assign_args.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/assign_args')
        w = -1.3
        _dw = ctypes.c_float(0)
        x = -3.0
        _dx = ctypes.c_float(0)
        y = 5.0
        _dy = ctypes.c_float(0)
        z = 3.0
        _dz = ctypes.c_float(0)
        dout = 2.7
        lib.d_assign_args(w,
                          ctypes.byref(_dw),
                          x,
                          ctypes.byref(_dx),
                          y,
                          ctypes.byref(_dy),
                          z,
                          ctypes.byref(_dz),
                          dout)

        w1 = 5.0
        x1 = w1 + x + y + z
        y1 = 6.0
        z1 = x1 * x1

        dz1 = dout
        dx1 = dz1 * 2 * x1
        dw1 = dx1
        dx = dx1
        dy = dx1
        dz = dx1
        dw = 0.0

        assert abs(_dw.value - dw) < epsilon and \
            abs(_dx.value - dx) < epsilon and \
            abs(_dy.value - dy) < epsilon and \
            abs(_dz.value - dz) < epsilon

    def test_refs_out(self):
        with open('loma_code/refs_out.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/refs_out')
        x = 0.7
        _dx = ctypes.c_float(0)
        _dy = 0.1
        lib.d_refs_out(x,
                       ctypes.byref(_dx),
                       _dy)

        assert abs(_dx.value - 0.1 * 2 * x) < epsilon

    def test_call_sin(self):
        with open('loma_code/call_sin.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_sin')
        x = 1.5
        _dx = ctypes.c_float(0)
        dout = -0.3
        lib.d_call_sin(x, ctypes.byref(_dx), dout)

        assert abs(_dx.value - dout * math.cos(x)) < epsilon

    def test_call_cos(self):
        with open('loma_code/call_cos.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_cos')
        x = 1.5
        _dx = ctypes.c_float(0)
        dout = -0.3
        lib.d_call_cos(x, ctypes.byref(_dx), dout)

        assert abs(_dx.value + dout * math.sin(x)) < epsilon

    def test_call_sqrt(self):
        with open('loma_code/call_sqrt.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_sqrt')
        x = 1.5
        _dx = ctypes.c_float(0)
        dout = -0.3
        lib.d_call_sqrt(x, ctypes.byref(_dx), dout)

        assert abs(_dx.value - (0.5 * dout / math.sqrt(x))) < epsilon

    def test_call_pow(self):
        with open('loma_code/call_pow.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_pow')
        x = 1.5
        _dx = ctypes.c_float(0)
        y = 0.7
        _dy = ctypes.c_float(0)
        dout = -0.3
        lib.d_call_pow(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        assert abs(_dx.value - dout * y * math.pow(x, y - 1)) < epsilon and \
            abs(_dy.value - dout * math.pow(x, y) * math.log(x)) < epsilon

    def test_call_exp(self):
        with open('loma_code/call_exp.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_exp')
        x = 1.5
        _dx = ctypes.c_float(0)
        dout = -0.3
        lib.d_call_exp(x, ctypes.byref(_dx), dout)

        assert abs(_dx.value - dout * math.exp(x)) < epsilon

    def test_call_log(self):
        with open('loma_code/call_log.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_log')
        x = 1.5
        _dx = ctypes.c_float(0)
        dout = -0.3
        lib.d_call_log(x, ctypes.byref(_dx), dout)

        assert abs(_dx.value - dout / x) < epsilon

    def test_call(self):
        with open('loma_code/call.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call')
        x = 1.5
        _dx = ctypes.c_float(0)
        y = 0.7
        _dy = ctypes.c_float(0)
        dout = -0.3
        lib.d_call(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        z0 = math.sin(x)
        z1 = math.cos(z0) + 1.0
        z2 = math.sqrt(z1) - y * y
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
        dy = -dz2 * 2 * y
        dz0 = -dz1 * math.sin(z0)
        dx = dz0 * math.cos(x)

        assert abs(_dx.value - dx) < epsilon and \
            abs(_dy.value - dy) < epsilon

    def test_int_input(self):
        with open('loma_code/int_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_input')
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 3
        _dy = ctypes.c_int(0)
        dout = 4.56
        lib.d_int_input(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        assert abs(_dx.value - dout * 5) < epsilon and \
            _dy.value == 0

    def test_int_output(self):
        with open('loma_code/int_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_output')
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 3
        _dy = ctypes.c_int(0)
        lib.d_int_output(x, ctypes.byref(_dx), y, ctypes.byref(_dy), 1)
        assert abs(_dx.value - 0) < epsilon

    def test_int_assign(self):
        with open('loma_code/int_assign.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_assign')
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 3
        _dy = ctypes.c_int(0)
        dout = 0.3
        lib.d_int_assign(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z0 = y
        # w = z0 * x
        # z1 = 6
        # return w * z1 * x + y - 1
        # -> y * x * 6 * x
        assert abs(_dx.value - dout * (2 * 6 * 3 * x)) < epsilon

    def test_array_output(self):
        with open('loma_code/array_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_output')
        x = 0.7
        _dx = ctypes.c_float(0)
        py_y = [0.0, 0.0]
        y = (ctypes.c_float * len(py_y))(*py_y)
        py_dy = [0.3, 0.5]
        _dy = (ctypes.c_float * len(py_dy))(*py_dy)
        lib.d_array_output(x, _dx, _dy)
        assert abs(_dx.value - (0.3 * 2 * x + 0.5 * 3 * x * x)) < epsilon

    def test_array_input(self):
        with open('loma_code/array_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_input')
        py_x = [0.7, 0.3]
        x = (ctypes.c_float * len(py_x))(*py_x)
        py_dx = [0.0, 0.0]
        _dx = (ctypes.c_float * len(py_dx))(*py_dx)
        dout = -0.27
        lib.d_array_input(x, _dx, dout)
        assert abs(_dx[0] - 2 * dout) < epsilon and \
            abs(_dx[1] - 6 * x[1] * dout) < epsilon

    def test_int_array_input(self):
        with open('loma_code/int_array_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/int_array_input')
        py_x = [0.7, 0.3]
        x = (ctypes.c_float * len(py_x))(*py_x)
        py_dx = [0.0, 0.0]
        _dx = (ctypes.c_float * len(py_dx))(*py_dx)
        py_y = [5]
        y = (ctypes.c_int * len(py_y))(*py_y)
        py_dy = [0]
        _dy = (ctypes.c_int * len(py_dy))(*py_dy)
        dout = 0.5
        lib.d_int_array_input(x, _dx, y, _dy, dout)
        assert abs(_dx[0] - dout) < epsilon and \
            abs(_dx[1] - dout) < epsilon

    def test_array_input_indexing(self):
        with open('loma_code/array_input_indexing.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_input_indexing')
        py_x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        x = (ctypes.c_float * len(py_x))(*py_x)
        py_dx = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        _dx = (ctypes.c_float * len(py_dx))(*py_dx)
        i = 1
        _di = ctypes.c_int(0)
        j = 3.5
        _dj = ctypes.c_float(0)
        dout = -0.5
        lib.d_array_input_indexing(\
            x, _dx, i, ctypes.byref(_di), j, ctypes.byref(_dj), dout)
        assert abs(_dx[1] - dout * x[3]) < epsilon and \
            abs(_dx[3] - dout * x[1]) < epsilon and \
            abs(_dx[2] - dout * x[6]) < epsilon and \
            abs(_dx[6] - dout * x[2]) < epsilon and \
            abs(_dx[4] - dout * x[5]) < epsilon and \
            abs(_dx[5] - dout * x[4]) < epsilon

    def test_array_output_indexing(self):
        with open('loma_code/array_output_indexing.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/array_output_indexing')
        x = 0.3
        _dx = ctypes.c_float(0)
        i = 1
        _di = ctypes.c_int(0)
        j = 3.5
        _dj = ctypes.c_float(0)
        py_dy = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        _dy = (ctypes.c_float * len(py_dy))(*py_dy)
        lib.d_array_output_indexing(\
            x, ctypes.byref(_dx), i, ctypes.byref(_di), j, ctypes.byref(_dj), _dy)
        # y[1] = x
        # y[3] = 2 * x
        # y[2] = 3 * x
        # y[6] = 4 * x
        assert abs(_dx.value - (0.2 + 0.4 * 2 + 0.3 * 3 + 0.7 * 4)) < epsilon and \
            abs(_dj.value - 0) < epsilon

    def test_sum_nested_array(self):
        with open('loma_code/sum_nested_array.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/sum_nested_array')
        pointer_arr = (ctypes.POINTER(ctypes.c_float) * 3)()
        _dpointer_arr = (ctypes.POINTER(ctypes.c_float) * 3)()
        arr0 = (ctypes.c_float * 3)(0.1, 0.2, 0.3)
        _darr0 = (ctypes.c_float * 3)(0.0, 0.0, 0.0)
        pointer_arr[0] = ctypes.cast(ctypes.pointer(arr0), ctypes.POINTER(ctypes.c_float))
        _dpointer_arr[0] = ctypes.cast(ctypes.pointer(_darr0), ctypes.POINTER(ctypes.c_float))
        arr1 = (ctypes.c_float * 2)(0.4, 0.5)
        _darr1 = (ctypes.c_float * 2)(0.0, 0.0)
        pointer_arr[1] = ctypes.cast(ctypes.pointer(arr1), ctypes.POINTER(ctypes.c_float))
        _dpointer_arr[1] = ctypes.cast(ctypes.pointer(_darr1), ctypes.POINTER(ctypes.c_float))
        arr2 = (ctypes.c_float * 1)(0.6)
        _darr2 = (ctypes.c_float * 1)(0.0)
        pointer_arr[2] = ctypes.cast(ctypes.pointer(arr2), ctypes.POINTER(ctypes.c_float))
        _dpointer_arr[2] = ctypes.cast(ctypes.pointer(_darr2), ctypes.POINTER(ctypes.c_float))
        dout = 0.3
        lib.d_sum_nested_array(pointer_arr, _dpointer_arr, dout)
        assert abs(_dpointer_arr[0][0] - 2 * dout * pointer_arr[0][0]) < epsilon and \
               abs(_dpointer_arr[0][1] - 2 * dout * pointer_arr[0][1]) < epsilon and \
               abs(_dpointer_arr[0][2] - 2 * dout * pointer_arr[0][2]) < epsilon and \
               abs(_dpointer_arr[1][0] - 2 * dout * pointer_arr[1][0]) < epsilon and \
               abs(_dpointer_arr[1][1] - 2 * dout * pointer_arr[1][1]) < epsilon and \
               abs(_dpointer_arr[2][0] - 2 * dout * pointer_arr[2][0]) < epsilon

    def test_struct_input(self):
        with open('loma_code/struct_input.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_input')
        Foo = structs['Foo']
        f = Foo(1.23, 3, 4.56)
        _df = Foo(0.0, 0, 0.0)
        dout = 0.3
        # out = 5 * foo.x + foo.y + foo.x * foo.z - 1
        lib.d_struct_input(f, ctypes.byref(_df), dout)
        assert abs(_df.x - dout * (5 + f.z)) < epsilon and \
            abs(_df.z - dout * (f.x))

    def test_struct_output(self):
        with open('loma_code/struct_output.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_output')

        Foo = structs['Foo']
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 3
        _dy = ctypes.c_int(0)
        dout = Foo(a=0.5,b=100)
        lib.d_struct_output(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # foo.a = x + y * x
        assert abs(_dx.value - 0.5 * (1 + 3)) < epsilon

    def test_struct_declare(self):
        with open('loma_code/struct_declare.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_declare')

        Foo = structs['Foo']
        f = Foo(a=1.23,b=3)
        _df = Foo(a=0.0,b=0)
        dout = Foo(a=0.3,b=100)
        lib.d_struct_declare(f, ctypes.byref(_df), dout)
        assert abs(_df.a - dout.a * 2) < epsilon

    def test_struct_assign(self):
        with open('loma_code/struct_assign.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/struct_assign')

        Foo = structs['Foo']
        f = Foo(a=1.23, b=3)
        _df = Foo(a=0.0, b=0)
        dout = Foo(a=0.3,b=100)
        lib.d_struct_assign(f, ctypes.byref(_df), dout)
        assert abs(_df.a - dout.a * 2) < epsilon

    def test_multivariate(self):
        with open('loma_code/multivariate.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/poly')
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

if __name__ == '__main__':
    unittest.main()
