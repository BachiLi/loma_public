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

def compile(func, filename = ''):
    ir = parser.parse(func)
    check.check_ir(ir)
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
        if isinstance(arg.t, loma_ir.Int):
            argtypes.append(ctypes.c_int)
        elif isinstance(arg.t, loma_ir.Float):
            argtypes.append(ctypes.c_float)
        elif isinstance(arg.t, loma_ir.Array):
            argtypes.append(ctypes.c_void_p)
        else:
            assert False
    c_func.argtypes = argtypes
    if ir.ret_type == loma_ir.Int():
        c_func.restype = ctypes.c_int
    elif ir.ret_type == loma_ir.Float():
        c_func.restype = ctypes.c_float
    elif ir.ret_type == None:
        c_func.restype = None
    else:
        assert False

    return lib
