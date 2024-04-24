import matplotlib.pyplot as plt
from matplotlib import animation
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes
import numpy as np

with open('loma_code/mass_spring_rev_loop.py') as f:
    structs, lib = compiler.compile(f.read(),
                              target = 'c',
                              output_filename = '_code/mass_spring_rev_loop')
gradH = lib.gradH
MassSpringConfig = structs['MassSpringConfig']

n = 40
q0x = np.linspace(0.0, 0.8, n, dtype = np.float32)
q0y = np.zeros(n, dtype = np.float32)
q0 = np.vstack((q0x, q0y)).reshape((-1, ), order='F')
p0 = np.zeros(2 * n, dtype = np.float32)
config = MassSpringConfig(mass = 1.0, length = 0.8 / (n-1), k = 1000.0, g = 4.0, n = n)
# time step
ts = 0.0001
# frame per second
fps = 20
# damping factor
damp = 0.025

def solver(t, q, p):
    # given a target time t and q/p, advances
    # q & p and output
    ct = 0
    while True:
        cur_ts = ts
        if ct + cur_ts >= t:
            cur_ts = t - ct
        # sympletic Euler: first advances p, then uses
        # p to advance q
        q_grad = np.zeros_like(q)
        p_grad = np.zeros_like(p)
        gradH(q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
              p.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
              config,
              q_grad.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
              p_grad.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),)
        next_p = p - cur_ts * q_grad
        next_q = q + cur_ts * p_grad
        q = next_q
        p = next_p
        ct += ts
        if ct >= t:
            break
    return ct, q, p

def visualize():
    fig = plt.figure(figsize=(8, 4))
    ax = plt.axes(xlim=(-1.5, 1.5), ylim=(-5, 1))
    line, = ax.plot([], [], '-', lw=2)
    point, = ax.plot([], [], 'g.', ms=3)

    t = 0
    q = q0
    p = p0
    def animate(i):
        nonlocal t, q, p
        dt, q, p = solver(1.0/fps, q, p)
        # don't move the first node so the animation is more interesting
        q[:2] = q0[:2]
        p[:2] = p0[:2]
        # some hacks to introduce damping to the system
        p[2:] = (1 - damp) * p[2:]

        t += dt
        n = int(len(q)/2)
        x = np.zeros(n)
        y = np.zeros(n)
        for i in range(n):
            x[i] = q[2 * i]
            y[i] = q[2 * i + 1]
        line.set_data(x, y)
        point.set_data(x, y)
        return point,

    return animation.FuncAnimation(fig, animate, frames=400, interval=fps, blit=True)

anim = visualize()
anim.save('mass_spring_rev_loop.mp4')
plt.show()
