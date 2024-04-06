import matplotlib.pyplot as plt
from matplotlib import animation
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes

with open('loma_code/pendulum_fwd.py') as f:
    structs, lib = compiler.compile(f.read(),
                              target = 'c',
                              output_filename = '_code/pendulum_fwd')
dHdq = lib.dHdq
dHdp = lib.dHdp
PendulumConfig = structs['PendulumConfig']

# Start at q = pi /4 and p = 0
q0 = math.pi / 4
p0 = 0.0
# radius = 20
r = 20.0
# mass = 1
m = 1.0
# gravitational constant
g = 9.8
# time step: 0.01
ts = 0.01
# frame per second
fps = 20

config = PendulumConfig(mass = m, radius = r, g = g)

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
        next_p = p - cur_ts * dHdq(q, p, config)
        next_q = q + cur_ts * dHdp(q, next_p, config)
        q = next_q
        p = next_p
        ct += ts
        if ct >= t:
            break
    return ct, q, p

def visualize():
    fig = plt.figure(figsize=(8, 4))
    ax = plt.axes(xlim=(-25, 25), ylim=(-25, 0))
    line, = ax.plot([], [], '-', lw=2)
    point, = ax.plot([], [], 'g.', ms=20)

    t = 0
    q = q0
    p = p0
    def animate(i):
        nonlocal t, q, p
        dt, q, p = solver(1.0/fps, q, p)
        x = r * math.sin(q)
        y = -r * math.cos(q)
        t += dt
        line.set_data([0, x], [0, y])
        point.set_data([x], [y])
        return point,

    return animation.FuncAnimation(fig, animate, frames=400, interval=fps, blit=True)

anim = visualize()
anim.save('single_pendulum_fwd.mp4')
plt.show()
