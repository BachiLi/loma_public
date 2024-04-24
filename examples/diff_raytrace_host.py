import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('loma_code/diff_raytrace.py') as f:
        structs, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/diff_raytrace')

    w = 400
    h = 225
    img = np.zeros([h, w, 3], dtype = np.single)
    lib.diff_raytrace(w, h, img.ctypes.data_as(ctypes.POINTER(structs['Vec3'])))
    plt.imshow(img)
    plt.show()
