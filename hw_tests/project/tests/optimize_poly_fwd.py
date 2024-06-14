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

with open('../loma_code/third_order_poly_fwd.py') as f:
    _, lib = compiler.compile(f.read(),target = 'c',output_filename = '_code/third_order_poly_fwd1')

f = lib.third_order_poly
# Plot the loss landscape
left = -3.0
right = 3.0
bottom = -3.0
top = 3.0
x = np.arange(left,right,0.1)
y = np.arange(bottom,top,0.1)
X,Y = np.meshgrid(x, y)
Z = np.zeros(X.shape)
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        Z[i, j] = f(X[i, j], Y[i,j])

with open('../loma_code/third_order_poly_fwd.py') as f:
    structs, lib = compiler.compile(f.read(),target = 'openMpi',output_filename = '_code/third_order_poly_fwd')
x = 2.0
y = 2.0
step_size = 0.5
_dfloat = structs['_dfloat']
num_worker = 2
px_x = [_dfloat(x, 1.0), _dfloat(x, 0.0)]
px_y = [_dfloat(y, 0.0), _dfloat(y, 1.0)]
input1 = (_dfloat * len(px_x))(*px_x)
input2 = (_dfloat * len(px_y))(*px_y)
py_y = [_dfloat(0, 0)] * num_worker
out = (_dfloat * len(py_y))(*py_y)
lib.mpi_runner(input1,input2,out,num_worker)
x1 = x - step_size* out[0].dval
y1 = y - step_size* out[1].dval


fig = plt.figure()
ax = plt.axes()

im = ax.imshow(Z, extent=[left,right,bottom,top])
plt.colorbar(im)
ax.plot([x,x1], [y,y1], color='red')

plt.show()
