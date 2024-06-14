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

class Homework1Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_subtract(self):
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
        # result = [(2.0,0.2),(1.0,0.2)]
        # for worker in range(num_worker):
        #     flag = False
        #     print(f"Result from Worker {worker+1}: val = {out[worker].val}, dval = {out[worker].dval}")
        #     for res in result:
        #         if abs(out[worker].val - res[0]) < epsilon and abs(out[worker].dval - res[1]) < epsilon:
        #             flag = True
        #             break
        #     assert flag

    # def test_while_loop_fwd(self):
    #     with open('../../hw3/loma_code/while_loop_fwd.py') as f:
    #         structs, lib = compiler.compile(f.read(),target = 'c',output_filename = '_code/while_loop_fwd1')
    #     _dfloat = structs['_dfloat']
    #     # x = _dfloat(1.23, 0.4)
    #     # n = 5
    #     input1 = [_dfloat(1.0, 0.5),_dfloat(2.0, 1.5)]
    #     input2 = [100000000,100000000]
    #     start_time = time.time()
    #     for i in range(len(input1)):
    #         out = lib.fwd_while_loop(input1[i], input2[i])
    #     end_time = time.time()
    #     print(f"Time taken for while loop: {end_time - start_time}")
    #     # assert abs(out.dval - x.dval * (math.cos(math.sin(math.sin(math.sin(math.sin(x.val))))) * \
    #     #                                 math.cos(math.sin(math.sin(math.sin(x.val))))) * \
    #     #                                 math.cos(math.sin(math.sin(x.val))) * \
    #     #                                 math.cos(math.sin(x.val)) * \
    #     #                                 math.cos(x.val)) < epsilon

if __name__ == '__main__':
    unittest.main()

