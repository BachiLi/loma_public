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
                                            target = 'openMpi',
                                            output_filename = '_code/identity')
        _dfloat = structs['_dfloat']
        num_worker = 2
        x = _dfloat(1.23, 4.56)
        py_y = [_dfloat(0, 0)] * num_worker
        out = (_dfloat * len(py_y))(*py_y)

        lib.mpi_runner(x, out, num_worker)
        for i in range(num_worker):
            assert abs(out[i].val - 1.23) < epsilon and abs(out[i].dval - 4.56) < epsilon


if __name__ == '__main__':
    unittest.main()

