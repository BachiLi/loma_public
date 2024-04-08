import matplotlib.pyplot as plt
import numpy as np
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes

with open('loma_code/third_order_poly_fwd.py') as f:
    _, lib = compiler.compile(f.read(),
                              target = 'c',
                              output_filename = '_code/third_order_poly_fwd')

f = lib.third_order_poly
grad_f = lib.grad_third_order_poly

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

# Actual gradient descent loop
# Start from (2, 2)
x, y = 2.0, 2.0
traj_x = [x]
traj_y = [y]
step_size = 1e-2
for i in range(2000):
    gx = ctypes.c_float(0)
    gy = ctypes.c_float(0)
    grad_f(x, y, gx, gy)
    x -= step_size * gx.value
    y -= step_size * gy.value
    traj_x.append(x)
    traj_y.append(y)
traj_x = np.array(traj_x)
traj_y = np.array(traj_y)

fig = plt.figure()
ax = plt.axes()

im = ax.imshow(Z, extent=[left,right,bottom,top])
plt.colorbar(im)
ax.plot(traj_x, traj_y, color='red')

plt.show()
