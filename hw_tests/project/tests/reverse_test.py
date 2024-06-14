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
epsilon = 1e-4


class Homework2Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # def test_identity_rev(self):
    #     with open('../loma_code/identity_rev.py') as f:
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

    # def test_constant(self):
    #     with open('../loma_code/constant_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/constant_rev')
    #     num_worker = 2
    #     py_x  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [5.0,1.0]
    #     dout =  [2.0,2.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for i in range(num_worker):
    #         print(f"Result from Worker {i+1}: {arg_dx[i]}")
    #         assert abs(arg_dx[i] - 0.0) < epsilon
    
    def test_plus_rev(self):
        with open('../loma_code/plus_rev.py') as f:
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

    # def test_subtract_rev(self):
    #     with open('../loma_code/subtract_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/subtract_rev')
    #     num_worker = 2
    #     py_x  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y  = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [5.0,1.0]
    #     y = [6.0,4.0]
    #     dout =  [3.0,4.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x,arg_dx,arg_y,arg_dy,arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker]) < epsilon and  abs(arg_dy[worker] + dout[worker]) < epsilon

    # def test_multiply_rev(self):
    #     with open("../loma_code/multiply_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/multiply_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [5.0, 1.0]
    #     y = [6.0, 4.0]
    #     dout = [3.0, 4.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert (
    #             abs(arg_dx[worker] - dout[worker] * y[worker]) < epsilon
    #             and abs(arg_dy[worker] - dout[worker] * x[worker]) < epsilon
    #         )

    # def test_divide_rev(self):
    #     with open("../loma_code/divide_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/divide_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [5.0, 1.0]
    #     y = [6.0, 4.0]
    #     dout = [3.0, 4.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert (
    #             abs(arg_dx[worker] - dout[worker] / y[worker]) < epsilon
    #             and abs(arg_dy[worker] + (dout[worker] * x[worker]) /(y*y)) < epsilon
    #         )

    # def test_square_rev(self):
    #     with open("../loma_code/square_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/square_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [5.0, 1.0]
    #     dout = [3.0, 4.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - 2 * dout[worker] * x[worker]) < epsilon

    # def test_declare_rev(self):
    #     with open("../loma_code/declare_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/declare_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [5.0, 1.0]
    #     y = [6.0, 4.0]
    #     dout = [3.0, 4.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)


    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         # simulate the reverse-diff program
    #         z0_val = x[worker] + y[worker]
    #         z1_val = z0_val + 5.0
    #         z2_val = z1_val * z0_val
    #         z3_val = z2_val / z1_val
    #         z4_val = z3_val - x[worker]

    #         z4_dval = dout[worker]
    #         # z4_val = z3_val - x
    #         z3_dval = dout[worker]
    #         x_dval = -dout[worker]
    #         # z3_val = z2_val / z1_val
    #         z2_dval = z3_dval / z1_val
    #         z1_dval = -z3_dval * z2_val / (z1_val * z1_val)
    #         # z2_val = z1_val * z0_val
    #         z1_dval += z2_dval * z0_val
    #         z0_dval = z2_dval * z1_val
    #         # z1_val = z0_val + 5.0
    #         z0_dval += z1_dval
    #         # z0_val = x + y
    #         x_dval += z0_dval
    #         y_dval = z0_dval
    #         assert abs(arg_dx[worker] - x_dval) < epsilon and \
    #             abs(arg_dy[worker] - y_dval) < epsilon

    # def test_assign_rev(self):
    #     with open("../loma_code/assign1_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/assign1_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [-3.0, -4.0]
    #     y = [5.0, 2.0]
    #     dout = [3.0, 1.0]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - 3 * dout[worker]) < epsilon and \
    #         abs(arg_dy[worker] - 5 * dout[worker]) < epsilon

    # def test_assign2_rev(self):
    #     with open("../loma_code/assign2_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/assign2_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [2.0, 1.0]
    #     y = [-6.0, -2.0]
    #     dout = [3.5, 2.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - (2.5 + y[worker]) * dout[worker]) < epsilon and \
    #         abs(arg_dy[worker] - (-3.0 + x[worker]) * dout[worker]) < epsilon

    # def test_assign3_rev(self):
    #     with open("../loma_code/assign3_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/assign3_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [2.0, 1.0]
    #     y = [-6.0, -4.0]
    #     dout = [3.5, 2.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - y[worker] * dout[worker]) < epsilon and \
    #         abs(arg_dy[worker]  - x[worker] * dout[worker]) < epsilon

    # def test_assign4_rev(self):
    #     with open("../loma_code/assign4_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/assign4_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [2.0, 1.0]
    #     y = [-6.0, -4.0]
    #     dout = [3.5, 2.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         z1 = 2.5 * x[worker] - 3.0 * y[worker]
    #         z2 = z1 * z1 + z1 * x[worker] * y[worker] + z1

    #         dz2 = dout[worker]
    #         dz1 = 2 * z1 * dz2 + x[worker] * y[worker] * dz2 + dz2
    #         dx = dz2 * z1 * y[worker]
    #         dy = dz2 * z1 * x[worker]
    #         dx += dz1 * 2.5
    #         dy -= dz1 * 3.0

    #         assert abs(arg_dx[worker] - dx) < epsilon and \
    #             abs(arg_dy[worker] - dy) < epsilon

    # def test_assign5_rev(self):
    #     with open("../loma_code/assign5_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/assign5_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [2.0, 1.0]
    #     y = [-6.0, -4.0]
    #     dout = [3.5, 2.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         z0 = x[worker] * y[worker]
    #         w0 = z0
    #         z1 = x[worker] + y[worker]
    #         w1 = w0 + z1 * z1
    #         z2 = 2 * x[worker]
    #         z3 = z2 + 1.0
    #         z4 = 3.0 * z3 * z3 + w1

    #         dz4 = dout[worker]
    #         dz3 = dz4 * 6.0 * z3
    #         dw1 = dz4
    #         dz2 = dz3
    #         dx = dz2 * 2
    #         dw0 = dw1
    #         dz1 = dw1 * z1 * 2
    #         dx += dz1
    #         dy = dz1
    #         dz0 = dw0
    #         dx += dz0 * y[worker]
    #         dy += dz0 * x[worker]

    #         assert abs(arg_dx[worker] - dx) < epsilon and \
    #             abs(arg_dy[worker] - dy) < epsilon
            
    # def test_assign_args(self):
    #     with open("../loma_code/assign_args_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/assign_args_rev"
    #         )
    #     num_worker = 2
    #     py_w = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_z = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     w =[-1.3, -0.3]
    #     x = [-3.0, -2.0]
    #     y = [5.0, 4.0]
    #     z = [3.0, 1.0]
    #     dout = [2.7, 3.7]
    #     arg_dw = (ctypes.c_float * len(py_w))(*py_w)
    #     arg_w = (ctypes.c_float * len(w))(*w)
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dz = (ctypes.c_float * len(py_z))(*py_z)
    #     arg_z = (ctypes.c_float * len(z))(*z)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_w, arg_dw, arg_x, arg_dx, arg_y, arg_dy, arg_z, arg_dz, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dw ={arg_dw[worker]}, dx = {arg_dx[worker]}, dy = {arg_dy[worker]}, dz ={arg_dz[worker]}")
    #         w1 = 5.0
    #         x1 = w1 + x[worker] + y[worker] + z[worker]
    #         y1 = 6.0
    #         z1 = x1 * x1

    #         dz1 = dout[worker]
    #         dx1 = dz1 * 2 * x1
    #         dw1 = dx1
    #         dx = dx1
    #         dy = dx1
    #         dz = dx1
    #         dw = 0.0

    #         assert abs(arg_dw[worker] - dw) < epsilon and \
    #             abs(arg_dx[worker] - dx) < epsilon and \
    #             abs(arg_dy[worker] - dy) < epsilon and \
    #             abs(arg_dz[worker] - dz) < epsilon

    # def test_refs_out_rev(self):
    #     with open("../loma_code/refs_out_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/refs_out_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [0.7, 0.2]
    #     dout = [0.1, 0.2]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] * 2 * x[worker]) < epsilon

    # def test_call_sin_rev(self):
    #     with open("../loma_code/call_sin_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_sin_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 2.5]
    #     dout = [-0.3, -0.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] * math.cos(x[worker])) < epsilon

    # def test_call_cos_rev(self):
    #     with open("../loma_code/call_cos_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_cos_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 2.5]
    #     dout = [-0.3, -0.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] + dout[worker] * math.sin(x[worker])) < epsilon

    # def test_call_cos_rev(self):
    #     with open("../loma_code/call_sqrt_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_sqrt_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 2.5]
    #     dout = [-0.3, -0.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - (0.5 * dout[worker] / math.sqrt(x[worker]))) < epsilon

    # def test_call_pow_rev(self):
    #     with open("../loma_code/call_pow_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_pow_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 2.5]
    #     y = [0.7, 0.8]
    #     dout = [-0.3, -0.4]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] * y[worker] * math.pow(x[worker], y[worker] - 1)) < epsilon and \
    #         abs(arg_dy[worker] - dout[worker] * math.pow(x[worker], y[worker]) * math.log(x[worker])) < epsilon

    # def test_call_exp_rev(self):
    #     with open("../loma_code/call_exp_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_exp_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 2.5]
    #     dout = [-0.3, -0.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] * math.exp(x[worker])) < epsilon

    # def test_call_log_rev(self):
    #     with open("../loma_code/call_log_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_log_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 2.5]
    #     dout = [-0.3, -0.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] / x[worker]) < epsilon

    # def test_call_rev(self):
    #     with open("../loma_code/call_rev.py") as f:
    #         structs, lib = compiler.compile(
    #             f.read(), target="openMpi", output_filename="_code/call_rev"
    #         )
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     x = [1.5, 1.6]
    #     y = [0.7, 0.8]
    #     dout = [-0.3, 2.5]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         z0 = math.sin(x[worker])
    #         z1 = math.cos(z0) + 1.0
    #         z2 = math.sqrt(z1) - y[worker] * y[worker]
    #         z3 = math.pow(z2, z1)
    #         z4 = math.exp(z3)
    #         z5 = math.log(z3 + z4)

    #         dz5 = dout[worker]
    #         dz3 = dout[worker] / (z3 + z4)
    #         dz4 = dout[worker] / (z3 + z4)
    #         dz3 += dz4 * z4
    #         dz2 = dz3 * z1 * math.pow(z2, z1 - 1)
    #         dz1 = dz3 * math.pow(z2, z1) * math.log(z2)
    #         dz1 += (0.5) * (dz2 / math.sqrt(z1))
    #         dy = -dz2 * 2 * y[worker]
    #         dz0 = -dz1 * math.sin(z0)
    #         dx = dz0 * math.cos(x[worker])

    #         assert abs(arg_dx[worker] - dx) < epsilon and \
    #             abs(arg_dy[worker] - dy) < epsilon

    # def test_int_input(self):
    #     with open('../loma_code/int_input_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/int_input_rev')
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [0,0]
    #     x = [1.23,1.23]
    #     y = [3, 3]
    #     dout = [4.56, 4.56]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_int * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_int * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] * 5) < epsilon and arg_dy[worker] == 0

    # def test_int_output(self):
    #     with open('../loma_code/int_output_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/int_output_rev')
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [0,0]
    #     x = [1.23,1.23]
    #     y = [3, 3]
    #     dout = [1,1]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_int * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_int * len(y))(*y)
    #     arg_dreturn = (ctypes.c_int * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - 0) < epsilon
        
    # def test_int_assign(self):
    #     with open('../loma_code/int_assign_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi', output_filename = '_code/int_assign_rev')
    #     num_worker = 2
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [0,0]
    #     x = [1.23,1.23]
    #     y = [3, 3]
    #     dout = [0.3, 0.3]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_int * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_int * len(y))(*y)
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)
    #     lib.mpi_runner(arg_x, arg_dx, arg_y, arg_dy, arg_dreturn, num_worker)
    #     # z0 = y
    #     # w = z0 * x
    #     # z1 = 6
    #     # return w * z1 * x + y - 1
    #     # -> y * x * 6 * x
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}, dy = {arg_dy[worker]}")
    #         assert abs(arg_dx[worker] - dout[worker] * (2 * 6 * 3 * x[worker])) < epsilon

    # def test_array_output(self):
    #     with open('../loma_code/array_output_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi', output_filename = '_code/array_output_rev')
    #     num_worker = 2
    #     x = [0.7,0.7]
    #     y = [0.0, 0.0,0.0, 0.0]
    #     py_x = [ctypes.c_float(0.0), ctypes.c_float(0.0)]
    #     py_y = [0.3, 0.5,0.3, 0.5]
    #     y_size = [2,2]
    #     py_size = [2,2]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dy = (ctypes.c_float * len(py_y))(*py_y)
    #     arg_y = (ctypes.c_float * len(y))(*y)
    #     arg_y_size = (ctypes.c_int * len(y_size))(*y_size)
    #     arg_py_size = (ctypes.c_int * len(py_size))(*py_size)
    #     lib.mpi_runner(arg_x, arg_dx,arg_dy, arg_py_size, num_worker)
    #     for worker in range(num_worker):
    #         print(f"Result from Worker {worker+1}: dx = {arg_dx[worker]}")
    #         assert abs(arg_dx[worker] - (0.3 * 2 * x[worker] + 0.5 * 3 * x[worker] * x[worker])) < epsilon

    # def test_array_input(self):
    #     with open('../loma_code/array_input_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/array_input_rev')
    #     num_worker = 2
    #     py_x = [0.7, 0.3] * num_worker
    #     x = (ctypes.c_float * len(py_x))(*py_x)
    #     py_x_size = [2,2]
    #     x_size = (ctypes.c_int * len(py_x_size))(*py_x_size)
    #     py_dx = [0.0, 0.0] * num_worker
    #     _dx = (ctypes.c_float * len(py_dx))(*py_dx)
    #     _dx_size = [2,2]
    #     dx_size = (ctypes.c_int * len(_dx_size))(*_dx_size)
    #     out = [-0.27,-0.27]
    #     dout = (ctypes.c_float * len(out))(*out)
    #     lib.mpi_runner(x, x_size, _dx, dx_size, dout, num_worker)
    #     temp = []
    #     for worker in range(len(py_x)):
    #         if worker < 2:
    #             print(f"Result from Worker {1}: dx = {_dx[worker]}")
    #         else:
    #             print(f"Result from Worker {2}: dx = {_dx[worker]}")
    #         temp.append(_dx[worker])
    #     j = 0
    #     for i in range(0,len(temp),2):
    #         assert abs(temp[i] - 2 * dout[j]) < epsilon and abs(temp[i+1] - 6 * x[i+1] * dout[j]) < epsilon
    #         j+=1

    # def test_int_array_input(self):
    #     with open('../loma_code/int_array_input_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/int_array_input_rev')
    #     num_worker = 2
    #     py_x = [0.7, 0.3] * num_worker
    #     x = (ctypes.c_float * len(py_x))(*py_x)
    #     py_x_size = [2,2]
    #     x_size = (ctypes.c_int * len(py_x_size))(*py_x_size)

    #     py_dx = [0.0, 0.0] * num_worker
    #     _dx = (ctypes.c_float * len(py_dx))(*py_dx)
    #     _dx_size = [2,2]
    #     dx_size = (ctypes.c_int * len(_dx_size))(*_dx_size)

    #     py_y = [5] *num_worker
    #     y = (ctypes.c_int * len(py_y))(*py_y)
    #     py_size = [1,1]
    #     y_size = (ctypes.c_int * len(py_size))(*py_size)

    #     py_dy = [0] * num_worker
    #     _dy = (ctypes.c_int * len(py_dy))(*py_dy)
    #     _dy_size = [1,1]
    #     dy_size = (ctypes.c_int * len(_dy_size))(*_dy_size)

    #     dout = [0.5,0.5]
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)

    #     lib.mpi_runner(x,x_size, _dx,dx_size, y,y_size, _dy,dy_size,arg_dreturn,num_worker)
    #     result= []
    #     for worker in range(len(py_dx)):
    #         print(f"Result from Worker {worker+1}: dx = {_dx[worker]}")
    #         result.append(_dx[worker])
        
    #     assert abs(result[0] - dout[0]) < epsilon and \
    #         abs(result[1] - dout[0]) < epsilon

    # def test_array_input_indexing(self):
    #     with open('../loma_code/array_input_indexing_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/array_input_indexing_rev')
    #     num_worker = 2
    #     py_x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] * num_worker
    #     x = (ctypes.c_float * len(py_x))(*py_x)
    #     py_x_size = [7,7]
    #     x_size = (ctypes.c_int * len(py_x_size))(*py_x_size)

    #     py_dx = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]* num_worker
    #     _dx = (ctypes.c_float * len(py_dx))(*py_dx)

    #     v = [1,1]
    #     input1 = (ctypes.c_int * len(v))(*v)
        
    #     _dv = [ctypes.c_int(0),ctypes.c_int(0)]
    #     input2 = (ctypes.c_int * len(_dv))(*_dv)
        
    #     c = [3.5,3.5]
    #     input3 = (ctypes.c_float * len(c))(*c)

    #     _dj = [ctypes.c_float(0),ctypes.c_float(0)]
    #     input4 = (ctypes.c_float * len(_dj))(*_dj)

    #     dout = [-0.5,-0.5]
    #     arg_dreturn = (ctypes.c_float * len(dout))(*dout)

    #     lib.mpi_runner(x,x_size, _dx,x_size, input1, input2, input3, input4, arg_dreturn, num_worker)
    #     result = []
    #     for i in range(len(py_x)):
    #         print(f"Result from Worker {i}: dx = {_dx[i]}")
    #         result.append(_dx[i])
    #     assert abs(result[1] - dout[0] * x[3]) < epsilon and \
    #         abs(result[3] - dout[0] * x[1]) < epsilon and \
    #         abs(result[2] - dout[0] * x[6]) < epsilon and \
    #         abs(result[6] - dout[0] * x[2]) < epsilon and \
    #         abs(result[4] - dout[0] * x[5]) < epsilon and \
    #         abs(result[5] - dout[0] * x[4]) < epsilon
            
if __name__ == "__main__":
    unittest.main()
