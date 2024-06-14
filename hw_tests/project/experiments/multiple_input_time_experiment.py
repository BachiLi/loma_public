import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(os.path.dirname(current)))
sys.path.append(parent)
import compiler
import ctypes
import error
import math
import gpuctypes.opencl as cl
import cl_utils
import unittest
import numpy as np
import matplotlib.pyplot as plt
import time
epsilon = 1e-4

class MultipleInput(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_subtract_openMpi(self):
        # Compile the OpenMPI code
        with open('../loma_code/subtract.py') as f:
            structs, lib = compiler.compile(f.read(), target='openMpi', output_filename='_code/subtract')
        
        _dfloat = structs['_dfloat']
        num_worker = 100
        # Test inputs
        px_x = [_dfloat(5.0, 0.5)] *10000
        px_y = [_dfloat(1.2, 0.3)] *10000

        input1 = (_dfloat * len(px_x))(*px_x)
        input2 = (_dfloat * len(px_y))(*px_y)
        py_y = [_dfloat(0, 0)] * num_worker
        out = (_dfloat * len(py_y))(*py_y)

        start_time = time.time()
        lib.mpi_runner(input1, input2, out, num_worker)
        mpi_end_time = time.time()
        print(f"Time taken for OpenMPI Implementation: {mpi_end_time - start_time:.6f} seconds")

    def test_subtract_normal(self):
        with open('../loma_code/subtract.py') as f:
            structs, lib = compiler.compile(f.read(), target='c', output_filename='_code/subtract1')
        _dfloat = structs['_dfloat']
        px_x = [_dfloat(5.0, 0.5)] * 10000
        px_y = [_dfloat(1.2, 0.3)] * 10000
        start_time = time.time()
        for i in range(len(px_x)):
            x = px_x[i]
            y = px_y[i]
            out_sub = lib.d_subtract(x, y)
        normal_end_time = time.time()

        print(f"Time taken for Normal Implementation: {normal_end_time - start_time:.6f} seconds")

if __name__ == '__main__':
    unittest.main()

