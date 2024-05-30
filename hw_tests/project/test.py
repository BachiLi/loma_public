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

    # def test_identity(self):
    #     with open('loma_code/identity.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/identity')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(1.23, 4.56)
    #     px_x = [x]
    #     dfloat_input = (_dfloat * len(px_x))(*px_x)
    #     x2 = 0
    #     px_x2 = [x2]
    #     int_input = (ctypes.c_int * len(px_x2))(*px_x2)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(dfloat_input, out, num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - 1.23) < epsilon and abs(out[i].dval - 4.56) < epsilon

    
    # def test_constant(self):
    #     with open('loma_code/constant.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/constant')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.23, 0.5), _dfloat(1.23, 0.3)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(x, out, num_worker)
    #     for i in range(num_worker):
    #         print(out[i].val,out[i].dval)
    #         assert abs(out[i].val - 2.0) < epsilon and abs(out[i].dval - 0.0) < epsilon

    # def test_plus(self):
    #     with open('loma_code/plus.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/plus')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 4
    #     px_x = [_dfloat(5.0, 0.5), _dfloat(6.0, 0.3),_dfloat(7.0, 0.2),_dfloat(8.0, 0.1)]
    #     px_y = [_dfloat(6.0, 1.5), _dfloat(7.0, 2.5),_dfloat(8.0, 3.5),_dfloat(9.0, 4.5)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_y))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2,out,num_worker)
    #     result = [(11,2),(13,2.8),(15,3.7),(17,4.6)]

    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag
    

    # def test_subtract(self):
    #     with open('loma_code/subtract.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/subtract')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(5.0, 0.5)
    #     y = _dfloat(6.0, 1.5)
    #     px_x = [x,y]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - (x.val - y.val)) < epsilon and abs(out[i].dval - (x.dval - y.dval)) < epsilon

    # def test_multiply(self):
    #     with open('loma_code/multiply.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/multiply')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(5.0, 0.5)
    #     y = _dfloat(6.0, 1.5)
    #     px_x = [x,y]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - (x.val * y.val)) < epsilon and abs(out[i].dval - (x.dval * y.val + x.val * y.dval)) < epsilon

    # def test_divide(self):
    #     with open('loma_code/divide.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/divide')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(5.0, 0.5)
    #     y = _dfloat(6.0, 1.5)
    #     px_x = [x,y]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - (x.val / y.val)) < epsilon and abs(out[i].dval - ((x.dval * y.val - x.val * y.dval)/(y.val * y.val))) < epsilon


    # def test_declare(self):
    #     with open('loma_code/declare.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/declare')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(5.0, 0.5)
    #     y = _dfloat(6.0, 1.5)
    #     px_x = [x,y]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     # simulate the forward-diff program
    #     z0_val = x.val + y.val
    #     z0_dval = x.dval + y.dval
    #     z1_val = z0_val + 5.0
    #     z1_dval = z0_dval + 0.0
    #     z2_val = z1_val * z0_val
    #     z2_dval = z1_dval * z0_val + z0_dval * z1_val
    #     for i in range(num_worker):
    #         assert abs(out[i].val - z2_val) < epsilon and abs(out[i].dval - z2_dval) < epsilon

    # def test_assign(self):
    #     with open('loma_code/assign.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/assign')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(-3.0, -1.0)
    #     y = _dfloat(5.0, 3.0)
    #     px_x = [x,y]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - (-3.0 + 5.0)) < epsilon and abs(out[i].dval - (-1.0 + 3.0)) < epsilon

    # def test_side_effect(self):
    #     with open('loma_code/side_effect.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/side_effect')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(-3.5, -1.5)
    #     y = _dfloat(7.0, 2.0)
    #     z = _dfloat(0.0, 0.0)
    #     px_x = [x,y,z]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - (x.val * y.val)) < epsilon and abs(out[i].dval - (x.dval * y.val + x.val * y.dval)) < epsilon
    

    # def test_call_sin(self):
    #     with open('loma_code/call_sin.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_sin')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(1.5, 0.3)
    #     y = _dfloat(0.0, 0.0)
    #     z = _dfloat(0.0, 0.0)
    #     px_x = [x,y,z]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     for i in range(num_worker):
    #         assert abs(out[i].val - math.sin(x.val)) < epsilon and abs(out[i].dval - x.dval * math.cos(x.val)) < epsilon


    # def test_int_input(self):
    #     with open('loma_code/int_input.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/int_input')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = _dfloat(5, 4)
    #     y = 3
    #     px_x = [_dfloat(5, 4),_dfloat(4, 3)]
    #     px_x2 = [y,y]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (ctypes.c_int * len(px_x2))(*px_x2)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = [(27,20), (22,15)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_array_input(self):
    #     with open('loma_code/array_input.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi', output_filename = '_code/array_input')
    #     _dfloat = structs['_dfloat']        
    #     num_worker = 2
    #     py_x = [_dfloat(0.7, 0.8), _dfloat(0.3, 0.5),_dfloat(0.3, 0.4), _dfloat(0.4, 0.6)]
    #     py_size = [2,2]
    #     input = (_dfloat * len(py_x))(*py_x)
    #     input2 = (ctypes.c_int * len(py_size))(*py_size)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, input2, out,num_worker)
    #     for i in range(num_worker):
    #         print(out[i].val,out[i].dval)
    #         # assert abs(out[i].val - (0.7 + 0.3)) < epsilon and abs(out[i].dval - (0.8 + 0.5)) < epsilon


    # def test_struct_input(self):
    #     with open('loma_code/struct_input.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/struct_input')
    #     _dfloat = structs['_dfloat']
    #     _dFoo = structs['_dFoo']
    #     num_worker = 2
    #     f = _dFoo(_dfloat(1, 4), 3)
    #     py_x = [_dFoo(_dfloat(1, 4), 3),_dFoo(_dfloat(2, 6), 5)]
    #     input = (_dFoo * len(py_x))(*py_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input,out,num_worker)
    #     result = [(7,20),(14,30)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_array_output(self):
    #     with open('loma_code/array_output.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/array_output')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     py_x = [_dfloat(0.7, 0.8),_dfloat(0.7, 0.8)]
    #     input = (_dfloat * len(py_x))(*py_x)
    #     py_y = [_dfloat(0.0, 0.0), _dfloat(0.0, 0.0)]* num_worker
    #     y = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, y,num_worker)
    #     for worker in range(num_worker):
    #         print(y[0][0].val,y[0][0].dval,y[1][1].val,y[1][1].dval)
    #     # assert abs(y[0].val - x.val * x.val) < epsilon and \
    #     #     abs(y[0].dval - 2 * x.val * x.dval) < epsilon and \
    #     #     abs(y[1].val - x.val * x.val * x.val) < epsilon and \
    #     #     abs(y[1].dval - 3 * x.val * x.val * x.dval) < epsilon

    # def test_identity_rev(self):
    #     with open('loma_code/identity_rev.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/identity_rev')
    #     num_worker = 2
    #     _dx=ctypes.c_float(0.0)
    #     _dx1=ctypes.c_float(0.0)
    #     py_x  = [_dx, _dx1]
    #     x = [1.23,1.23]
    #     dx = [4.56,4.56]
    #     arg_dx = (ctypes.c_float * len(py_x))(*py_x)
    #     arg_x = (ctypes.c_float * len(x))(*x)
    #     arg_dreturn = (ctypes.c_float * len(dx))(*dx)
    #     lib.mpi_runner(arg_x,arg_dx,arg_dreturn, num_worker)
    #     for i in range(num_worker):
    #         assert abs(arg_dx[i] - 4.56) < epsilon

    def test_plus_rev(self):
        with open('loma_code/plus_rev.py') as f:
            structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/plus_rev')
        num_worker = 2
        _dx=ctypes.c_float(0.0)
        _dx1=ctypes.c_float(0.0)
        _dy=ctypes.c_float(0.0)
        _dy1=ctypes.c_float(0.0)
        py_x  = [_dx, _dx1]
        py_y  = [_dy, _dy1]
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
            assert abs(arg_dx[i] - dout[i]) < epsilon and  abs(arg_dy[i] - dout[i]) < epsilon
        

if __name__ == '__main__':
    unittest.main()

