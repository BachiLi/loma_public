import ctypes
from ctypes import CDLL
import codegen
import inspect
import os
import parser
import shutil
from subprocess import run

def compile(func, filename = ''):
    ir = parser.parse(func)
    code = codegen.codegen(ir)

    # determine the filename to dump to
    caller_frame = inspect.stack()[1]
    if filename == '':
        caller_dir  = os.path.dirname(caller_frame.filename)
        try:
            os.mkdir(os.path.join(caller_dir, '_code'))
        except FileExistsError:
            pass
        filename = os.path.join(caller_dir, '_code',
                                f"{ir.name}.so")
    print(code)

    log = run(['g++', '-shared', '-fPIC', '-o', filename, '-O2', '-x', 'c++', '-'],
        input = code,
        encoding='utf-8',
        capture_output=True)
    if log.returncode != 0:
        print(log.stderr)

    lib = CDLL(filename)
    c_func = getattr(lib, ir.name)
    argtypes = []
    for arg in ir.args:
        argtypes.append(ctypes.c_float)
    c_func.argtypes = argtypes
    c_func.restype = ctypes.c_float

    return lib

