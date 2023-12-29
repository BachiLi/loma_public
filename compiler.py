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

def loma_to_ctypes_type(t, ctypes_structs):
    match t:
        case loma_ir.Int():
            return ctypes.c_int
        case loma_ir.Float():
            return ctypes.c_float
        case loma_ir.Array():
            return ctypes.c_void_p
        case loma_ir.Struct():
            return ctypes_structs[t.id]
        case None:
            return None
        case _:
            assert False

def compile(loma_code, output_filename):
    structs, funcs = parser.parse(loma_code)
    check.check_ir(structs, funcs)
    code = codegen.codegen(structs, funcs)

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

    # Sort the struct topologically
    # TODO: maybe extract this as a common function
    sorted_structs_list = []
    traversed_struct = set()
    def traverse_structs(s):
        if s in traversed_struct:
            return
        for m in s.members:
            if isinstance(m.t, loma_ir.Struct): 
                traverse_structs(structs[m.t.id])
        sorted_structs_list.append(s)
        traversed_struct.add(s)
    for s in structs.values():
        traverse_structs(s)

    # build ctypes structs/classes
    ctypes_structs = {}
    for s in sorted_structs_list:
        ctypes_structs[s.id] = type(s.id, (ctypes.Structure, ), {
            '_fields_': [(m.id, loma_to_ctypes_type(m.t, ctypes_structs)) for m in s.members]
        })

    lib = CDLL(output_filename)
    for f in funcs.values():
        c_func = getattr(lib, f.id)
        c_func.argtypes = \
            [loma_to_ctypes_type(arg.t, ctypes_structs) for arg in f.args]
        c_func.restype = loma_to_ctypes_type(f.ret_type, ctypes_structs)

    return ctypes_structs, lib
