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
import numpy as np

epsilon = 1e-4

class Homework3Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_ifelse_fwd(self):
        with open('loma_code/ifelse_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.4)
        y = _dfloat(1, 0.5)
        z = lib.fwd_ifelse(x, y)
        assert abs(z.val - 5 * x.val) < epsilon and \
            abs(z.dval - 5 * x.dval) < epsilon

        # test both branches
        x = _dfloat(1.23, 0.4)
        y = _dfloat(-1, 0.5)
        z = lib.fwd_ifelse(x, y)
        assert abs(z.val - 2 * x.val) < epsilon and \
            abs(z.dval - 2 * x.dval) < epsilon

    def test_ifelse_rev(self):
        with open('loma_code/ifelse_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_rev')
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 5 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

        # test both branches
        x = 1.23
        _dx = ctypes.c_float(0)
        y = -1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 2 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

    def test_ifelse_side_effects_rev(self):
        with open('loma_code/ifelse_side_effects_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_side_effects_rev')
        
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse_side_effects(x, _dx, y, _dy, 0.3)

        assert abs(_dx.value - 0.3 * math.cos(5.0 * x) * 5) < epsilon and \
            abs(_dy.value) < epsilon

        # test both branches
        x = 1.23
        _dx = ctypes.c_float(0)
        y = -1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse_side_effects(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 2 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

    def test_nested_ifelse_rev(self):
        with open('loma_code/nested_ifelse_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_ifelse_rev')
        
        # test all three branches
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 1
        _dy = ctypes.c_float(0)
        lib.rev_nested_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 0.3 * math.cos(5.0 * x) * 5) < epsilon and \
            abs(_dy.value) < epsilon

        x = -1.23
        _dx = ctypes.c_float(0)
        y = 1
        _dy = ctypes.c_float(0)
        lib.rev_nested_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value + 0.3 * math.sin(5.0 * x) * 5) < epsilon and \
            abs(_dy.value) < epsilon

        x = 1.23
        _dx = ctypes.c_float(0)
        y = -1
        _dy = ctypes.c_float(0)
        lib.rev_nested_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 2 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

    def test_func_call_fwd(self):
        with open('loma_code/func_call_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        y = _dfloat(0.5, 0.5)
        z = lib.fwd_func_call(x, y)
        # z = 2 * (x * x * y + y * y)
        # dz = 2 * (2 * dx * x * y + x * x * dy + 2 * dy * y)
        assert abs(z.val - 2 * (x.val * x.val * y.val + y.val * y.val)) < epsilon and \
            abs(z.dval - 2 * (2 * x.dval * x.val * y.val + x.val * x.val * y.dval + 2 * y.dval * y.val)) < epsilon

    def test_chained_calls_fwd(self):
        with open('loma_code/chained_calls_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/chained_calls_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        out = lib.fwd_chained_calls(x)

        # out = sin(2 * x * x)
        # dout = dx * cos(2 * x * x) * 4 * x 
        assert abs(out.dval - (x.dval * math.cos(2 * x.val * x.val) * 4 * x.val)) < epsilon

    def test_call_stmt_fwd(self):
        with open('loma_code/call_stmt_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        z = lib.fwd_call_stmt(x)
        # z = 2 * (x * x + x)
        # dout = 2 * dx * (2 * x + 1)
        assert abs(z.dval - (2 * x.dval * (2 * x.val + 1))) < epsilon

    def test_func_call_rev(self):
        with open('loma_code/func_call_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.5
        _dy = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_func_call(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z = 2 * (x * x * y + y * y)
        # dx = 4 * x * y * dout
        # dy = 2 * x^2 * dout + 2 * y * dout
        assert abs(_dx.value - (4 * x * y * dout)) < epsilon and \
            abs(_dy.value - dout * (2 * x * x + 2 * y))

    def test_func_call_rev2(self):
        with open('loma_code/func_call_rev2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_rev2')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.5
        _dy = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_func_call(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z = 2 * ((x + y) * (x * y))
        # dx = 2 * dout * ((x * y) + (x + y) * y)
        # dy = 2 * dout * ((x * y) + (x + y) * x)
        assert abs(_dx.value - (2 * dout * ((x * y) + (x + y) * y))) < epsilon and \
            abs(_dy.value - (2 * dout * ((x * y) + (x + y) * x))) < epsilon

    def test_func_call_assign_rev(self):
        with open('loma_code/func_call_assign_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_assign_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.5
        _dy = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_func_call_assign(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z = 2 * x * x * y * y
        # dx = dout * 4 * x * y^2
        # dy = dout * 4 * x^2 * y
        assert abs(_dx.value - dout * 4 * x * y * y) < epsilon and \
            abs(_dy.value - dout * 4 * x * x * y) < epsilon

    def test_call_array_rev(self):
        with open('loma_code/call_array_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_array_rev')
        x = ctypes.c_float(0)
        _dx = ctypes.c_float(0)
        _dout = 0.3
        z = lib.rev_call_array(ctypes.pointer(x),
                               ctypes.pointer(_dx),
                               _dout)
        # y = (x * x + x)
        # dx = dy * (2 * x + 1)
        assert abs(_dx.value - (_dout * (2 * x.value + 1))) < epsilon

    def test_call_stmt_rev(self):
        with open('loma_code/call_stmt_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_call_stmt(x, ctypes.byref(_dx), dout)
        # y = 2 * (x * x + x)
        # dx = 2 * dout * (2 * x + 1)
        assert abs(_dx.value - (2 * dout * (2 * x + 1))) < epsilon

    def test_call_stmt2_rev(self):
        with open('loma_code/call_stmt2_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt2_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        _dy = 0.3
        z = lib.rev_call_stmt2(x, ctypes.byref(_dx), _dy)
        # y = (x * x + x)
        # dx = dy * (2 * x + 1)
        assert abs(_dx.value - (_dy * (2 * x + 1))) < epsilon

    def test_call_stmt_side_effects(self):
        with open('loma_code/call_stmt_side_effects.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_side_effects')
        x = 0.67
        _dx = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_call_stmt_side_effects(x, ctypes.byref(_dx), dout)
        # y = 2 * (x * x + x) + 10 * x
        # dx = dout * (2 * (2 * x + 1) + 10)
        assert abs(_dx.value - (dout * (2 * (2 * x + 1) + 10))) < epsilon

    def test_call_stmt_side_effects2(self):
        with open('loma_code/call_stmt_side_effects2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_side_effects2')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.89
        _dy = ctypes.c_float(0)
        dout = 0.3
        out = lib.rev_call_stmt_side_effects2(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        # out = 2 * (x * x + x) + (0.5 * y)^2 * x
        # dx = dout * (2 * (2 * x + 1) + (0.5 * y)^2)
        # dy = dout * (0.5 * y) * x
        assert abs(_dx.value - (dout * (2 * (2 * x + 1) + 0.25 * y * y))) < epsilon and \
            abs(_dy.value - (dout * (0.5 * y * x))) < epsilon

    def test_call_stmt_array_rev(self):
        with open('loma_code/call_stmt_array_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_array_rev')
        x = ctypes.c_float(0)
        _dx = ctypes.c_float(0)
        _dy = ctypes.c_float(0.3)
        z = lib.rev_call_stmt_array(ctypes.pointer(x),
                                    ctypes.pointer(_dx),
                                    ctypes.pointer(_dy))
        # y = (x * x + x)
        # dx = dy * (2 * x + 1)
        assert abs(_dx.value - (_dy.value * (2 * x.value + 1))) < epsilon

    def test_chained_calls_rev(self):
        with open('loma_code/chained_calls_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/chained_calls')
        x = 0.67
        _dx = ctypes.c_float(0)
        dout = 0.3
        out = lib.rev_chained_calls(x, ctypes.byref(_dx), dout)

        # out = sin(2 * x * x)
        # dx = dout * cos(2 * x * x) * 4 * x 
        assert abs(_dx.value - (dout * math.cos(2 * x * x) * 4 * x)) < epsilon

    def test_while_loop_fwd(self):
        with open('loma_code/while_loop_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/while_loop_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.4)
        n = 5
        out = lib.fwd_while_loop(x, n)

        # out = sin(sin(sin(sin(sin(x)))))
        # dout = dx * (cos(sin(sin(sin(sin(x))))) *
        #              cos(sin(sin(sin(x)))) *
        #              cos(sin(sin(x))) *
        #              cos(sin(x)) *
        #              cos(x))
        assert abs(out.dval - x.dval * (math.cos(math.sin(math.sin(math.sin(math.sin(x.val))))) * \
                                        math.cos(math.sin(math.sin(math.sin(x.val))))) * \
                                        math.cos(math.sin(math.sin(x.val))) * \
                                        math.cos(math.sin(x.val)) * \
                                        math.cos(x.val)) < epsilon

    def test_while_loop_rev(self):
        with open('loma_code/while_loop_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/while_loop_rev')
        x = 1.23
        _dx = ctypes.c_float(0)
        n = 5
        _dn = ctypes.c_int(0)
        dout = 0.4
        out = lib.rev_while_loop(x, _dx, n, _dn, dout)

        # out = sin(sin(sin(sin(sin(x)))))
        # dx = dout * (cos(sin(sin(sin(sin(x))))) *
        #              cos(sin(sin(sin(x)))) *
        #              cos(sin(sin(x))) *
        #              cos(sin(x)) *
        #              cos(x))
        assert abs(_dx.value - dout * (math.cos(math.sin(math.sin(math.sin(math.sin(x))))) * \
                                       math.cos(math.sin(math.sin(math.sin(x))))) * \
                                       math.cos(math.sin(math.sin(x))) * \
                                       math.cos(math.sin(x)) * \
                                       math.cos(x)) < epsilon

    def test_nested_while_loop_rev(self):
        with open('loma_code/nested_while_loop_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_while_loop_rev')
        x = 1.23
        _dx = ctypes.c_float(0)
        n = 5
        _dn = ctypes.c_int(0)
        dout = 0.4
        lib.rev_nested_while_loop(x, _dx, n, _dn, dout)

        # out = x + (n * (n-1)) * x^2
        # dx = dout * (1 + x * (n * (n - 1)))
        assert abs(_dx.value - dout * (x * (n * (n - 1)))) < epsilon

    def test_three_level_while_loop_rev(self):
        with open('loma_code/three_level_while_loop_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/three_level_while_loop_rev')
        x = 0.123
        _dx = ctypes.c_float(0)
        n = 5
        _dn = ctypes.c_int(0)
        dout = 0.4
        lib.rev_three_level_while_loop(x, _dx, n, _dn, dout)

        # out = x + n^3 * x^2
        # dx = dout * (1 + 2 * x * n^3))
        assert abs(_dx.value - dout * (1 + 2 * x * n * n * n)) < epsilon

    def test_parallel_copy(self):
        with open('loma_code/parallel_copy.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'ispc',
                                            output_filename = '_code/parallel_copy')
        x = 0.123
        n = 10000
        _dx = ctypes.c_float(0)
        np.random.seed(1234)
        _dz = np.random.random(n).astype('f') / n
        lib.rev_parallel_copy(x,
            ctypes.byref(_dx),
            _dz.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n)

        assert abs(_dx.value - np.sum(_dz)) < epsilon

    def test_parallel_add(self):
        with open('loma_code/parallel_add.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'ispc',
                                            output_filename = '_code/parallel_add')

        np.random.seed(seed=1234)
        n = 10000
        x = np.random.random(n).astype('f') / n
        _dx = np.zeros_like(x)
        y = np.random.random(n).astype('f') / n
        _dy = np.zeros_like(y)
        z = np.zeros_like(x)
        _dz = np.random.random(n).astype('f') / n
        lib.rev_parallel_add(
            x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            _dx.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            y.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            _dy.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            _dz.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n)

        assert np.sum(np.abs(_dx - _dz)) / n < epsilon and \
            np.sum(np.abs(_dy - _dz)) / n < epsilon

    def test_parallel_reduce(self):
        with open('loma_code/parallel_reduce.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'ispc',
                                            output_filename = '_code/parallel_reduce')

        np.random.seed(1234)
        n = 10000
        x = np.random.random(n).astype('f') / n
        _dx = np.zeros_like(x)
        _dz = 0.234
        lib.rev_parallel_reduce(\
            x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            _dx.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            _dz,
            n)

        assert np.sum(np.abs(_dx - _dz)) / n < epsilon

if __name__ == '__main__':
    unittest.main()
