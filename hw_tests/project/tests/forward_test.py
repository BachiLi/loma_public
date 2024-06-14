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

class Homework1Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # def test_identity(self):
    #     with open('../loma_code/identity.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/identity')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.23, 4.56), _dfloat(2.31, 3.14)]
    #     dfloat_input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(dfloat_input, out, num_worker)
    #     result = [(1.23,4.56),(2.31,3.14)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_constant(self):
    #     with open('../loma_code/constant.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '../_code/constant')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.23, 0.5), _dfloat(3.0, 0.3)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1, out, num_worker)
    #     result = [(2.0,0.0),(2.0,0.0)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_plus(self):
    #     with open('../loma_code/plus.py') as f:
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
    #     with open('../loma_code/subtract.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/subtract')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(5.0, 0.5),_dfloat(5.0, 1.5)]
    #     px_y = [_dfloat(3.0, 0.3),_dfloat(4.0, 1.3)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_x))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = [(2.0,0.2),(1.0,0.2)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_multiply(self):
    #     with open('../loma_code/multiply.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/multiply')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(5.0, 0.5),_dfloat(5.0, 1.5)]
    #     px_y = [_dfloat(3.0, 0.3),_dfloat(4.0, 1.3)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_x))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = [(15.0,3.0),(20.0,12.5)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_divide(self):
    #     with open('../loma_code/divide.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/divide')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(5.0, 0.5),_dfloat(5.0, 1.5)]
    #     px_y = [_dfloat(6.0, 1.5),_dfloat(4.0, 1.3)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_x))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = [(0.8333333134651184,-0.125),(1.25,-0.03125)]
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag


    # def test_declare(self):
    #     with open('../loma_code/declare.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/declare')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(5.0, 0.5),_dfloat(5.0, 0.5)]
    #     px_y = [_dfloat(6.0, 1.5),_dfloat(6.0, 1.5)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_x))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     # simulate the forward-diff program
    #     result = []
    #     for i in range(num_worker):
    #         z0_val = px_x[i].val + px_y[i].val
    #         z0_dval = px_x[i].dval + px_y[i].dval
    #         z1_val = z0_val + 5.0
    #         z1_dval = z0_dval + 0.0
    #         z2_val = z1_val * z0_val
    #         z2_dval = z1_dval * z0_val + z0_dval * z1_val
    #         result.append((z2_val,z2_dval))
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_assign(self):
    #     with open('../loma_code/assign.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/assign')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(-3.0, -1.0),_dfloat(4.0, 3.0)]
    #     px_y = [_dfloat(5.0, 3.0),_dfloat(6.0, -2.0)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_x))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = px_x[i].val + px_y[i].val
    #         dval = px_x[i].dval + px_y[i].dval
    #         result.append((val,dval))
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_side_effect(self):
    #     with open('../loma_code/side_effect.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/side_effect')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(-3.5, -1.5),_dfloat(-1.5, 4.5)]
    #     px_y = [_dfloat(7.0, 2.0),_dfloat(-3.5, -1.5)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_x))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1, input2, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = px_x[i].val * px_y[i].val
    #         dval = px_x[i].dval * px_y[i].val + px_x[i].val * px_y[i].dval
    #         result.append((val,dval))
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag
    

    # def test_call_sin(self):
    #     with open('../loma_code/call_sin.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_sin')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.5, 0.3), _dfloat(3.5, 0.6)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = math.sin(px_x[i].val) 
    #         dval = px_x[i].dval * math.cos(px_x[i].val)
    #         result.append((val,dval))
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag


    # def test_call_cos(self):
    #     with open('../loma_code/call_cos.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_cos')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.5, 0.3), _dfloat(3.5, 0.6)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = math.sin(px_x[i].val) 
    #         dval = px_x[i].dval * math.cos(px_x[i].val)
    #         result.append((val,dval))
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag


    # def test_call_sqrt(self):
    #     with open('../loma_code/call_sqrt.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_sqrt')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.5, 0.3), _dfloat(3.5, 0.6)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = math.sqrt(px_x[i].val)
    #         dval = (0.5 * px_x[i].dval / math.sqrt(px_x[i].val))
    #         result.append((val,dval))
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_call_pow(self):
    #     with open('../loma_code/call_pow.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_pow')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.5, 0.3), _dfloat(3.5, 0.6)]
    #     px_y = [_dfloat(0.7, 0.4), _dfloat(0.2, 0.3)]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (_dfloat * len(px_y))(*px_y)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2,out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = math.pow(px_x[i].val, px_y[i].val)
    #         dval = px_x[i].dval * px_y[i].val * math.pow(px_x[i].val, px_y[i].val - 1) + \
    #             px_y[i].dval * math.pow(px_x[i].val, px_y[i].val) * math.log(px_x[i].val)
    #         result.append((val,dval))
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_call_exp(self):
    #     with open('../loma_code/call_exp.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_exp')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.5, 0.3), _dfloat(3.5, 0.6)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = math.exp(px_x[i].val)
    #         dval = px_x[i].dval * math.exp(px_x[i].val)
    #         result.append((val,dval))
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_call_log(self):
    #     with open('../loma_code/call_log.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call_log')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.5, 0.3), _dfloat(3.5, 0.6)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = math.log(px_x[i].val)
    #         dval = px_x[i].dval / px_x[i].val
    #         result.append((val,dval))
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag
       
    # def test_call(self):
    #     with open('../loma_code/call.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/call')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [ _dfloat(1.5, 1.2), _dfloat(3.5, 0.6)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         z0_val = math.sin(px_x[i].val)
    #         z0_dval = math.cos(px_x[i].val) * px_x[i].dval
    #         z1_val = math.cos(z0_val) + 1.0
    #         z1_dval = -math.sin(z0_val) * z0_dval
    #         z2_val = math.sqrt(z1_val)
    #         z2_dval = z1_dval / (2 * math.sqrt(z1_val))
    #         z3_val = math.pow(z2_val, z1_val)
    #         z3_dval = z2_dval * z1_val * math.pow(z2_val, z1_val - 1) \
    #                 + z1_dval * math.pow(z2_val, z1_val) * math.log(z2_val)
    #         z4_val = math.exp(z3_val)
    #         z4_dval = math.exp(z3_val) * z3_dval
    #         z5_val = math.log(z3_val + z4_val)
    #         z5_dval = (z3_dval + z4_dval) / (z3_val + z4_val)
    #         result.append((z5_val,z5_dval))
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag


    # def test_int_input(self):
    #     with open('../loma_code/int_input.py') as f:
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

    # def test_int_output(self):
    #     with open('../loma_code/int_output.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/int_output')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(1.23, 4.56), _dfloat(2.5, 3.6)]
    #     px_y = [3,3]
    #     input1 = (_dfloat * len(px_x))(*px_x)
    #     input2 = (ctypes.c_int * len(px_y))(*px_y)
    #     py_y = [0] * num_worker
    #     out = (ctypes.c_int * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = 5 * px_x[i].val + px_y[i] - 1
    #         result.append(int(val))
    #     print(result)
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker]}")
    #         for res in result:
    #             if abs(out[worker] - res) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_array_output(self):
    #     with open('../loma_code/array_output.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/array_output')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     px_x = [_dfloat(2.0, 3.0),_dfloat(3.0, 4.0)]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     py_y = [_dfloat(0.0, 0.0), _dfloat(0.0, 0.0)]* num_worker
    #     py_size = [2]* num_worker
    #     input2 = (ctypes.c_int * len(py_size))(*py_size)
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, out,input2,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         for j in range(2):
    #             if j == 0:
    #                 val = px_x[i].val * px_x[i].val
    #                 dval = 2 * px_x[i].val * px_x[i].dval
    #             if j ==1:
    #                 val = px_x[i].val * px_x[i].val * px_x[i].val
    #                 dval = 3 * px_x[i].val * px_x[i].val * px_x[i].dval
    #             result.append((val,dval))
    #     for worker in range(len(py_y)):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_array_input(self):
    #     with open('../loma_code/array_input.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi', output_filename = '_code/array_input')
    #     _dfloat = structs['_dfloat']        
    #     num_worker = 2
    #     px_x = [_dfloat(0.7, 0.8), _dfloat(0.3, 0.5),_dfloat(0.3, 0.4), _dfloat(0.4, 0.6)]
    #     py_size = [2,2]
    #     input = (_dfloat * len(px_x))(*px_x)
    #     input2 = (ctypes.c_int * len(py_size))(*py_size)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input, input2, out,num_worker)
    #     result = []
    #     for i in range(0,num_worker+1,2):
    #         result.append((px_x[i].val + px_x[i+1].val,px_x[i].dval + px_x[i+1].dval))

    #     print(result)
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_int_array_input(self):
    #     with open('../loma_code/int_array_input.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/int_array_input')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     py_x = [_dfloat(0.7, 0.8), _dfloat(0.3, 0.5),_dfloat(0.9, 0.5), _dfloat(0.4, 0.1)]
    #     x = (_dfloat * len(py_x))(*py_x)
    #     py_x_size = [2,2]
    #     input1 = (ctypes.c_int * len(py_x_size))(*py_x_size)
    #     py_y = [5,4]
    #     y = (ctypes.c_int * len(py_y))(*py_y)
    #     py_y_size = [1,1]
    #     input2 = (ctypes.c_int * len(py_y_size))(*py_y_size)
    #     py_y_out = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y_out))(*py_y_out)
    #     lib.mpi_runner(x,input1,y, input2, out,num_worker)
    #     result = []
    #     l=0
    #     for i in range(num_worker):
    #         result.append((py_x[l].val + py_x[l+1].val + py_y[i] ,py_x[l].dval + py_x[l+1].dval))
    #         l+=2
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag


    # def test_array_input_indexing(self):
    #     with open('../loma_code/array_input_indexing.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/array_input_indexing')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     py_x = [_dfloat(0.1, 0.9),_dfloat(0.2, 0.8),_dfloat(0.3, 0.7),_dfloat(0.4, 0.6),_dfloat(0.5, 0.5),_dfloat(0.6, 0.4),_dfloat(0.7, 0.3)] * num_worker
    #     x = (_dfloat * len(py_x))(*py_x)
    #     py_x_size = [7,7]
    #     input1 = (ctypes.c_int * len(py_x_size))(*py_x_size)
    #     v = [1,1]
    #     c = [_dfloat(3.5, 0.5),_dfloat(3.5, 0.5)]
    #     input2 = (ctypes.c_int * len(v))(*v)
    #     input3 = (_dfloat * len(c))(*c)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(x,input1,input2,input3, out,num_worker)
    #     result = []
    #     for i in range(0,len(py_x),7):
    #         result.append((py_x[i+1].val + py_x[i+3].val + py_x[i+2].val + py_x[i+6].val, py_x[i+1].dval + py_x[i+3].dval + py_x[i+2].dval + py_x[i+6].dval))
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_array_output_indexing(self):
    #     with open('../loma_code/array_output_indexing.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/array_output_indexing')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = [_dfloat(0.3, 0.4),_dfloat(0.3, 0.4)]
    #     px_x = (_dfloat * len(x))(*x)
        
    #     v = [1,1]
    #     input1 = (ctypes.c_int * len(v))(*v)
        
    #     c = [_dfloat(3.5, 0.5),_dfloat(3.5, 0.5)]
    #     input2 = (_dfloat * len(c))(*c)
        
    #     py_y = [_dfloat(0, 0)] * 7 * num_worker
    #     y = (_dfloat * len(py_y))(*py_y)
        
    #     py_size = [7]* num_worker
    #     input3 = (ctypes.c_int * len(py_size))(*py_size)
        
    #     lib.mpi_runner(px_x,input1,input2,y,input3,num_worker)
    #     result = []
    #     for i in range(num_worker*7):
    #         result.append(_dfloat(0.0))
    #     multipliers = [0, 1, 3, 2, 0, 0, 4, 0, 1, 3, 2, 0, 0, 4]
    #     n_results = len(multipliers)
        
    #     for i in range(n_results):
    #         result[i].val = multipliers[i] * px_x[0].val
    #         result[i].dval = multipliers[i] * px_x[0].dval

    #     for worker in range(len(result)):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {y[worker].val}, dval = {y[worker].dval}")
    #         if abs(y[worker].val - result[worker].val) < epsilon and abs(y[worker].dval - result[worker].dval) < epsilon:
    #             flag = True
    #         assert flag

    # def test_multiple_outputs(self):
    #     with open('../loma_code/multiple_outputs.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/multiple_outputs')
    #     _dfloat = structs['_dfloat']
    #     num_worker = 2
    #     x = [_dfloat(0.7, 0.8),_dfloat(0.7, 0.8)]
    #     input1 = (_dfloat * len(x))(*x)

    #     px_y = [_dfloat(0.0, 0.0), _dfloat(0.0, 0.0),_dfloat(0.0, 0.0), _dfloat(0.0, 0.0)]
    #     input2 = (_dfloat * len(px_y))(*px_y)

    #     px_y_size = [2,2]
    #     input3 = (ctypes.c_int * len(px_y_size))(*px_y_size)

    #     z = [_dfloat(0.5, -0.3),_dfloat(0.5, -0.3)]
    #     input4 = (_dfloat * len(z))(*z)

    #     px_z_size = [1,1]
    #     input5 = (ctypes.c_int * len(px_z_size))(*px_z_size)

    #     lib.mpi_runner(input1,input2,input3,input4,input5,num_worker)
    #     result = []
    #     result2 = []
    #     for i in range(num_worker):
    #         val = x[i].val * x[i].val
    #         dval = 2 * x[i].val * x[i].dval
    #         val2 = x[i].val * x[i].val * x[i].val
    #         dval2 = 3 * x[i].val * x[i].val * x[i].dval
    #         result.append((val,dval))
    #         result.append((val2,dval2))
    #         result2.append((val*val2,val*dval2 + dval*val2))
        
    #     for worker in range(len(px_y)):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {input2[worker].val}, dval = {input2[worker].dval}")
    #         if abs(input2[worker].val - result[worker][0]) < epsilon and abs(input2[worker].dval - result[worker][1]) < epsilon:
    #             flag = True
    #         assert flag
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {input4[worker].val}, dval = {input4[worker].dval}")
    #         if abs(input4[worker].val - result2[worker][0]) < epsilon and abs(input4[worker].dval - result2[worker][1]) < epsilon:
    #             flag = True
    #         assert flag

    # def test_struct_input(self):
    #     with open('../loma_code/struct_input.py') as f:
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

    # def test_nested_struct_input(self):
    #     with open('../loma_code/nested_struct_input.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/nested_struct_input')
    #     _dfloat = structs['_dfloat']
    #     _dFoo = structs['_dFoo']
    #     _dBar = structs['_dBar']
    #     num_worker = 2
    #     f = _dFoo(_dfloat(1.23, 4.56), _dBar(3, _dfloat(1.23, 4.56)))
    #     f2 = _dFoo(_dfloat(1.23, 4.56), _dBar(3, _dfloat(1.23, 4.56)))
    #     py_x = [f,f2]
    #     input = (_dFoo * len(py_x))(*py_x)
    #     py_y = [_dfloat(0, 0)] * num_worker
    #     out = (_dfloat * len(py_y))(*py_y)
    #     lib.mpi_runner(input,out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = (py_x[i].x.val + py_x[i].y.z + py_x[i].y.w.val + 5) * 3
    #         dval = (py_x[i].x.dval + py_x[i].y.w.dval) * 3
    #         result.append((val,dval))
        
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
    #         for res in result:
    #             if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_struct_output(self):
    #     with open('../loma_code/struct_output.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/struct_output')
    #     _dfloat = structs['_dfloat']
    #     _dFoo = structs['_dFoo']
    #     num_worker = 2
    #     x = [_dfloat(1.23, 4.56),_dfloat(1.23, 4.56)]
    #     input1 = (_dfloat * len(x))(*x)
    #     y = [3,3]
    #     input2 = (ctypes.c_int * len(y))(*y)
    #     py_y = [_dFoo(_dfloat(0, 0), 0)] * num_worker
    #     out = (_dFoo * len(py_y))(*py_y)
    #     lib.mpi_runner(input1,input2, out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = x[i].val + y[i] * x[i].val
    #         dval = x[i].dval + y[i] * x[i].dval
    #         val2 = int(y[i] - x[i].val)
    #         result.append(_dFoo((val,dval),val2))

    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].a.val}, dval = {out[worker].a.dval}, int = {out[worker].b}")
    #         for res in result:
    #             if abs(out[worker].a.val - res.a.val) < epsilon and abs(out[worker].b - res.b) < epsilon and abs(out[worker].a.dval - res.a.dval) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_struct_declare(self):
    #     with open('../loma_code/struct_declare.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/struct_declare')
    #     _dfloat = structs['_dfloat']
    #     _dFoo = structs['_dFoo']
    #     num_worker = 2
    #     py_x = [_dFoo(a=_dfloat(1.23,4.56), b=3),_dFoo(a=_dfloat(1.23,4.56), b=3)]
    #     input = (_dFoo * len(py_x))(*py_x)
    #     py_y = [_dFoo(a=_dfloat(0, 0), b=0)] * num_worker
    #     out = (_dFoo * len(py_y))(*py_y)
    #     lib.mpi_runner(input,out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = py_x[i].a.val * 2
    #         dval = 2 * py_x[i].a.dval
    #         val2 = py_x[i].b 
    #         result.append(_dFoo((val,dval),val2))
    
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].a.val}, dval = {out[worker].a.dval}, int = {out[worker].b}")
    #         for res in result:
    #             if abs(out[worker].a.val - res.a.val) < epsilon and abs(out[worker].b - res.b) < epsilon and abs(out[worker].a.dval - res.a.dval) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

    # def test_struct_assign(self):
    #     with open('../loma_code/struct_assign.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/struct_assign')
    #     _dfloat = structs['_dfloat']
    #     _dFoo = structs['_dFoo']
    #     num_worker = 2
    #     py_x = [_dFoo(a=_dfloat(1.23,4.56), b=3),_dFoo(a=_dfloat(1.23,4.56), b=3)]
    #     input = (_dFoo * len(py_x))(*py_x)
    #     py_y = [_dFoo(a=_dfloat(0, 0), b=0)] * num_worker
    #     out = (_dFoo * len(py_y))(*py_y)
    #     lib.mpi_runner(input,out,num_worker)
    #     result = []
    #     for i in range(num_worker):
    #         val = py_x[i].a.val * 2
    #         dval = 2 * py_x[i].a.dval
    #         val2 = py_x[i].b 
    #         result.append(_dFoo((val,dval),val2))
    
    #     for worker in range(num_worker):
    #         flag = False
    #         print(f"Result from Worker {worker+1}: val = {out[worker].a.val}, dval = {out[worker].a.dval}, int = {out[worker].b}")
    #         for res in result:
    #             if abs(out[worker].a.val - res.a.val) < epsilon and abs(out[worker].b - res.b) < epsilon and abs(out[worker].a.dval - res.a.dval) < epsilon:
    #                 flag = True
    #                 break
    #         assert flag

if __name__ == '__main__':
    unittest.main()

