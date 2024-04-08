import matplotlib.pyplot as plt
import numpy as np
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes

with open('loma_code/bigger_poly_rev.py') as f:
    _, lib = compiler.compile(f.read(),
                              target = 'c',
                              output_filename = '_code/bigger_poly_rev')

f = lib.bigger_poly
grad_f = lib.grad_bigger_poly

# Gradient descent loop
np.random.seed(1234)
x = np.random.random(5).astype(np.float32)
print(x.dtype)
step_size = 1e-2
loss = [f(x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))]
for i in range(1000):
    gx = np.zeros(5, dtype=np.float32)
    grad_f(x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
           gx.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
    x -= step_size * gx
    loss.append(f(x.ctypes.data_as(ctypes.POINTER(ctypes.c_float))))

plt.plot(np.arange(len(loss)), np.array(loss))
plt.ylabel('loss')
plt.xlabel('iteration')
plt.show()

