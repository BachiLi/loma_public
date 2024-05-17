import matplotlib.pyplot as plt
import numpy as np
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes

with open('loma_code/third_order_poly_hess.py') as f:
    _, lib = compiler.compile(f.read(),
                              target = 'c',
                              output_filename = '_code/third_order_poly_hess')

f = lib.third_order_poly
grad_f = lib.grad_third_order_poly
hess_f = lib.hess_third_order_poly

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

# Actual Newton's method loop
# Start from (2, 2)
x, y = 2.0, 2.0
traj_x = [x]
traj_y = [y]
step_size = 1
for i in range(20):
    gx = ctypes.c_float(0)
    gy = ctypes.c_float(0)
    grad_f(x, y, gx, gy)
    hxx = ctypes.c_float(0)
    hxy = ctypes.c_float(0)
    hyy = ctypes.c_float(0)
    hess_f(x, y, hxx, hxy, hyy)
    # solve for H d = g
    inv_det = 1 / (hxx.value * hyy.value - hxy.value * hxy.value)
    hinv_xx = hyy.value * inv_det
    hinv_xy = -hxy.value * inv_det
    hinv_yy = hxx.value * inv_det
    dx = hinv_xx * gx.value + hinv_xy * gy.value
    dy = hinv_xy * gx.value + hinv_yy * gy.value
    x -= step_size * dx
    y -= step_size * dy
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
