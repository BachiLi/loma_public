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

class Homework3Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_ifelse_fwd(self):
        with open('loma_code/ifelse_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_fwd.so')
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
                                            output_filename = '_code/ifelse_rev.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        y = _dfloat(1, 0.0)
        lib.rev_ifelse(x, y, 0.3)
        assert abs(x.dval - 5 * 0.3) < epsilon and \
            abs(y.dval) < epsilon

        # test both branches
        x = _dfloat(1.23, 0.0)
        y = _dfloat(-1, 0.0)
        lib.rev_ifelse(x, y, 0.3)
        assert abs(x.dval - 2 * 0.3) < epsilon and \
            abs(y.dval) < epsilon

    def test_ifelse_side_effects_rev(self):
        with open('loma_code/ifelse_side_effects_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_side_effects_rev.so')
        
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        y = _dfloat(1, 0.0)
        lib.rev_ifelse_side_effects(x, y, 0.3)
        assert abs(x.dval - 0.3 * math.cos(5.0 * x.val) * 5) < epsilon and \
            abs(y.dval) < epsilon

        # test both branches
        x = _dfloat(1.23, 0.0)
        y = _dfloat(-1, 0.0)
        lib.rev_ifelse_side_effects(x, y, 0.3)
        assert abs(x.dval - 2 * 0.3) < epsilon and \
            abs(y.dval) < epsilon

    def test_nested_ifelse_rev(self):
        with open('loma_code/nested_ifelse_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_ifelse_rev.so')
        
        # test all three branches
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.0)
        y = _dfloat(1, 0.0)
        lib.rev_nested_ifelse(x, y, 0.3)
        assert abs(x.dval - 0.3 * math.cos(5.0 * x.val) * 5) < epsilon and \
            abs(y.dval) < epsilon

        _dfloat = structs['_dfloat']
        x = _dfloat(-1.23, 0.0)
        y = _dfloat(1, 0.0)
        lib.rev_nested_ifelse(x, y, 0.3)
        assert abs(x.dval + 0.3 * math.sin(5.0 * x.val) * 5) < epsilon and \
            abs(y.dval) < epsilon

        x = _dfloat(1.23, 0.0)
        y = _dfloat(-1, 0.0)
        lib.rev_nested_ifelse(x, y, 0.3)
        assert abs(x.dval - 2 * 0.3) < epsilon and \
            abs(y.dval) < epsilon

    def test_func_call_fwd(self):
        with open('loma_code/func_call_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_fwd.so')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        y = _dfloat(0.5, 0.5)
        z = lib.fwd_func_call(x, y)
        # z = 2 * (x * x * y + y * y)
        # dz = 2 * (2 * dx * x * y + x * x * dy + 2 * dy * y)
        assert abs(z.val - 2 * (x.val * x.val * y.val + y.val * y.val)) < epsilon and \
            abs(z.dval - 2 * (2 * x.dval * x.val * y.val + x.val * x.val * y.dval + 2 * y.dval * y.val)) < epsilon

if __name__ == '__main__':
    unittest.main()
