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
import matplotlib.pyplot as plt
epsilon = 1e-4

class Homework2Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    # def test_identity_rev(self):
    #     with open('loma_code/identity_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/identity_rev')
    #     num_worker = 2
    #     py_x  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.23,1.23]
    #     dx = [4.56,4.56]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dx))(*dx)
    #     lib.mpi_runner(arg_x,arg_dx,arg_dreturn, num_worker)
    #     for i in range(num_worker):
    #         print(f"Result from Worker {i+1}: {arg_dx[i]}")
    #         assert abs(arg_dx[i] - 4.56) < epsilon

    def test_plus_rev(self):
        with open('loma_code/plus_rev.py') as f:
            structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/plus_rev')
        num_worker = 2
        py_x  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
        py_y  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
        x = [5.0,1.0]
        y = [6.0,4.0]
        dout =  [3.0,4.0]
        arg_dx = (ctypes.c_float * len(py_x))(*py_x)
        arg_x = (ctypes.c_float * len(x))(*x)
        arg_dy = (ctypes.c_float * len(py_y))(*py_y)
        arg_y = (ctypes.c_float * len(y))(*y)
        arg_dreturn = (ctypes.c_float * len(dout))(*dout)
        lib.mpi_runner(arg_x,arg_dx,arg_y,arg_dy,arg_dreturn, num_worker)
        for i in range(num_worker):
            print(f"Result from Worker {i+1}: {arg_dx[i]}")
            assert abs(arg_dx[i] - dout[i]) < epsilon and  abs(arg_dy[i] - dout[i]) < epsilon

if __name__ == '__main__':
        unittest.main()