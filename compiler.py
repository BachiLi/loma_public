import attrs
import autodiff
import ctypes
from ctypes import CDLL
import check
import codegen_c
import codegen_ispc
import codegen_opencl
import inspect
import os
import parser
import shutil
from subprocess import run
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import numpy as np
import cl_utils
import pathlib

def loma_to_ctypes_type(t, ctypes_structs):
    match t:
        case loma_ir.Int():
            return ctypes.c_int
        case loma_ir.Float():
            return ctypes.c_float
        case loma_ir.Array():
            return ctypes.POINTER(loma_to_ctypes_type(t.t, ctypes_structs))
        case loma_ir.Struct():
            return ctypes_structs[t.id]
        case None:
            return None
        case _:
            assert False

def compile(loma_code,
            target = 'c',
            output_filename = None,
            opencl_context = None,
            opencl_device = None,
            opencl_command_queue = None):
    structs, funcs = parser.parse(loma_code)
    check.check_ir(structs, funcs, check_diff = False)
    structs, funcs = autodiff.differentiate(structs, funcs)
    check.check_ir(structs, funcs, check_diff = True)
    
    # Sort the struct topologically
    # TODO: maybe extract this as a common function
    sorted_structs_list = []
    traversed_struct = set()
    def traverse_structs(s):
        if s in traversed_struct:
            return
        for m in s.members:
            if isinstance(m.t, loma_ir.Struct) or isinstance(m.t, loma_ir.Array):
                next_s = m.t if isinstance(m.t, loma_ir.Struct) else m.t.t
                if isinstance(next_s, loma_ir.Struct):
                    traverse_structs(structs[next_s.id])
        sorted_structs_list.append(s)
        traversed_struct.add(s)
    for s in structs.values():
        traverse_structs(s)

    if output_filename is not None:
        pathlib.Path(os.path.dirname(output_filename)).mkdir(parents=True, exist_ok=True)

    # Generate and compile the code
    if target == 'c':
        code = codegen_c.codegen_c(structs, funcs)
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
    elif target == 'ispc':
        code = codegen_ispc.codegen_ispc(structs, funcs)

        print(code)

        obj_filename = output_filename + '.o'
        log = run(['ispc', '--pic', '-o', obj_filename, '-O2', '-'],
            input = code,
            encoding='utf-8',
            capture_output=True)
        if log.returncode != 0:
            print(log.stderr)

        script_dir = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))
        tasksys_path = os.path.join(script_dir, 'runtime', 'tasksys.cpp')

        output_dir = os.path.dirname(output_filename)
        tasksys_obj_path = os.path.join(output_dir, 'tasksys.o')
        log = run(['g++', '-c', '-o', output_filename, '-O2', '-o', tasksys_obj_path, tasksys_path],
            encoding='utf-8',
            capture_output=True)
        if log.returncode != 0:
            print(log.stderr)        

        log = run(['g++', '-shared', '-o', output_filename, '-O2', obj_filename, tasksys_obj_path],
            encoding='utf-8',
            capture_output=True)
        if log.returncode != 0:
            print(log.stderr)
    elif target == 'opencl':
        code = codegen_opencl.codegen_opencl(structs, funcs)

        print(code)
        
        kernel_names = [func_name for func_name, func in funcs.items() if func.is_simd]
        lib = cl_utils.cl_compile(opencl_context,
                                  opencl_device,
                                  opencl_command_queue,
                                  code,
                                  kernel_names)
    else:
        assert False, f'unrecognized compilation target {target}'

    # build ctypes structs/classes
    ctypes_structs = {}
    for s in sorted_structs_list:
        ctypes_structs[s.id] = type(s.id, (ctypes.Structure, ), {
            '_fields_': [(m.id, loma_to_ctypes_type(m.t, ctypes_structs)) for m in s.members]
        })

    # load the dynamic library
    if target == 'c' or target == 'ispc':
        lib = CDLL(output_filename)
        for f in funcs.values():
            c_func = getattr(lib, f.id)
            c_func.argtypes = \
                [loma_to_ctypes_type(arg.t, ctypes_structs) for arg in f.args]
            c_func.restype = loma_to_ctypes_type(f.ret_type, ctypes_structs)

    return ctypes_structs, lib
