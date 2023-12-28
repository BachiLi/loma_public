import ctypes
from ctypes import CDLL
import check
import codegen
import inspect
import os
import parser
import shutil
from subprocess import run
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def compile(loma_code, output_filename):
    ir = parser.parse(loma_code)
    check.check_ir(ir)
    code = codegen.codegen(ir)

    # add standard headers
    code = """
#include <math.h>
    \n""" + code

    print(code)

    log = run(['g++', '-shared', '-fPIC', '-o', output_filename, '-O2', '-x', 'c++', '-'],
        input = code,
        encoding='utf-8',
        capture_output=True)
    if log.returncode != 0:
        print(log.stderr)

    lib = CDLL(output_filename)
    for f in ir.defs:
        c_func = getattr(lib, f.name)
        argtypes = []
        for arg in f.args:
            if isinstance(arg.t, loma_ir.Int):
                argtypes.append(ctypes.c_int)
            elif isinstance(arg.t, loma_ir.Float):
                argtypes.append(ctypes.c_float)
            elif isinstance(arg.t, loma_ir.Array):
                argtypes.append(ctypes.c_void_p)
            else:
                assert False
        c_func.argtypes = argtypes
        if f.ret_type == loma_ir.Int():
            c_func.restype = ctypes.c_int
        elif f.ret_type == loma_ir.Float():
            c_func.restype = ctypes.c_float
        elif f.ret_type == None:
            c_func.restype = None
        else:
            assert False

    return lib
