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

def test_identity():
    with open('loma_code/identity.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/identity.so')
    assert abs(lib.d_identity() - 1) < 1e-6

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    test_identity()