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

class Homework1Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_while(self):
        with open('../loma_code/while.py') as f:
            structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/while')
        _dfloat = structs['_dfloat']
        num_worker = 100
        px_x = [_dfloat(1.0, 0.5)]*num_worker
        px_y = [100000]*num_worker
        input1 = (_dfloat * len(px_x))(*px_x)
        input2 = (ctypes.c_int * len(px_y))(*px_y)
        py_y = [_dfloat(0, 0)] * num_worker
        out = (_dfloat * len(py_y))(*py_y)
        start_time = time.time()
        lib.mpi_runner(input1,input2, out,num_worker)
        end_time = time.time()
        print(f"Time taken for while loop: {end_time - start_time}")
        for i in range(num_worker):
            print(out[i].val,out[i].dval)

    def test_while_loop_fwd(self):
        with open('../../hw3/loma_code/while_loop_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),target = 'c',output_filename = '_code/while_loop_fwd1')
        _dfloat = structs['_dfloat']
        input1 = [_dfloat(1.0, 0.5),_dfloat(2.0, 1.5)]
        input2 = [100000,100000]
        start_time = time.time()
        for i in range(len(input1)):
            out = lib.fwd_while_loop(input1[i], input2[i])
        end_time = time.time()
        print(f"Time taken for while loop: {end_time - start_time}")

if __name__ == '__main__':
    unittest.main()

