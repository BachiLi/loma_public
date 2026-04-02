import attrs
import autodiff
import ctypes
from ctypes import CDLL
import check
import codegen_c
import codegen_ispc
import codegen_slang
import inspect
import os
import parser
import shutil
from subprocess import run
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import numpy as np
import pathlib
import error
import platform
import distutils.ccompiler
import slangpy

def loma_to_ctypes_type(t : loma_ir.type | loma_ir.arg,
                        ctypes_structs : dict[str, ctypes.Structure]) -> ctypes.Structure:
    """ Given a loma type, maps to the corresponding ctypes type by
        looking up ctypes_structs
    """

    match t:
        case loma_ir.Arg():
            if isinstance(t.t, loma_ir.Array):
                return loma_to_ctypes_type(t.t, ctypes_structs)
            else:
                if t.i == loma_ir.Out():
                    return ctypes.POINTER(loma_to_ctypes_type(t.t, ctypes_structs))
                else:
                    return loma_to_ctypes_type(t.t, ctypes_structs)
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

def topo_sort_structs(structs : dict[str, loma_ir.Struct]):
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
    return sorted_structs_list

def compile(loma_code : str,
            target : str = 'c',
            output_filename : str = None,
            slang_device = None,
            print_error = True):
    """ Given loma frontend code represented as a string,
        compiles it to either C, ISPC, or Slang code.
        Furthermore, generates a library from the compiled code,
        and dynamically links the generated library.

        Parameters:
        loma_code - a string representing loma code to be compiled
        target - 'c', 'ispc', or 'slang'
        output_filename - where to store the generated library for C and ISPC backends. 
            Don't need the suffix (like '.so').
            when target == 'slang', this argument is ignored.
        slang_device - see slang_utils.create_device()
                    only used by the slang backend
        print_error - whether it prints compile errors or not
    """

    # The compiler passes
    # first parse the frontend code
    try:
        structs, funcs = parser.parse(loma_code)
        # next figure out the types related to differentiation
        structs, diff_structs, funcs = autodiff.resolve_diff_types(structs, funcs)
        # next check if the resulting code is valid, barring from the derivative code
        check.check_ir(structs, diff_structs, funcs, check_diff = False)
    except error.UserError as e:
        if print_error:
            print('[Error] error found before automatic differentiation:')
            print(e.to_string())
        raise e
    # next actually differentiate the functions
    funcs = autodiff.differentiate(structs, diff_structs, funcs)
    try:
        # next check if the derivative code is valid
        check.check_ir(structs, diff_structs, funcs, check_diff = True)
    except error.UserError as e:
        if print_error:
            print('[Error] error found after automatic differentiation:')
            print(e.to_string())
        raise e

    if output_filename is not None:
        # + .dll or + .so
        output_filename = output_filename + distutils.ccompiler.new_compiler().shared_lib_extension
        pathlib.Path(os.path.dirname(output_filename)).mkdir(parents=True, exist_ok=True)

    # Generate and compile the code
    if target == 'c':
        code = codegen_c.codegen_c(structs, funcs)
        # add standard headers
        code = """
#include <math.h>
        \n""" + code

        print('Generated C code:')
        print(code)

        if platform.system() == 'Windows':
            tmp_c_filename = f'_tmp.c'
            with open(tmp_c_filename, 'w') as f:
                f.write(code)
            obj_filename = output_filename + '.o'
            log = run(['cl.exe', '/c', '/O2', f'/Fo:{obj_filename}', tmp_c_filename],
                encoding='utf-8',
                capture_output=True)
            if log.returncode != 0:
                print(log.stderr)
            exports = [f'/EXPORT:{f.id}' for f in funcs.values()]
            log = run(['link.exe', '/DLL', f'/OUT:{output_filename}', '/OPT:REF', '/OPT:ICF', *exports, obj_filename],
                encoding='utf-8',
                capture_output=True)
            if log.returncode != 0:
                print(log.stderr)
            os.remove(tmp_c_filename)
        else:
            log = run(['gcc', '-shared', '-fPIC', '-o', output_filename, '-O2', '-x', 'c', '-'],
                input = code,
                encoding='utf-8',
                capture_output=True)
            if log.returncode != 0:
                print(log.stderr)
    elif target == 'ispc':
        code = codegen_ispc.codegen_ispc(structs, funcs)
        # add atomic add
        code = """
void atomic_add(float *ptr, float val) {
    float found = *ptr;
    float expected;
    do {
        expected = found;
        found = atomic_compare_exchange_global(ptr, expected, expected + val);
    } while (found != expected);
}
        \n""" + code

        print('Generated ISPC code:')
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

        if platform.system() == 'Windows':
            log = run(['cl.exe', '/std:c++17', '/c', '/O2', f'/Fo:{tasksys_obj_path}', tasksys_path],
                encoding='utf-8',
                capture_output=True)
            if log.returncode != 0:
                print(log.stderr)
            exports = [f'/EXPORT:{f.id}' for f in funcs.values()]
            log = run(['link.exe', '/DLL', f'/OUT:{output_filename}', '/OPT:REF', '/OPT:ICF', *exports, obj_filename, tasksys_obj_path],
                encoding='utf-8',
                capture_output=True)
            if log.returncode != 0:
                print(log.stderr)
        else:
            log = run(['g++', '-fPIC', '-std=c++17', '-c', '-O2', '-o', tasksys_obj_path, tasksys_path],
                encoding='utf-8',
                capture_output=True)
            if log.returncode != 0:
               print(log.stderr)
            log = run(['g++', '-fPIC', '-shared', '-o', output_filename, '-O2', obj_filename, tasksys_obj_path],
                encoding='utf-8',
                capture_output=True)
    elif target == 'slang':
        code = codegen_slang.codegen_slang(structs, funcs)
        print('Generated Slang code:')
        print(code)

        module = slangpy.Module.load_from_source(\
            slang_device,
            name = '_tmp',
            source = code)
        entry_points = [module.module.entry_point(func_name) for \
            func_name, func in funcs.items() if func.is_simd]
        kernels = {}
        for entry_point in entry_points:
            kernels[entry_point.name] = slang_device.create_compute_kernel(\
                slang_device.link_program([module.module], [entry_point]))
    else:
        assert False, f'unrecognized compilation target {target}'

    # load the dynamic library
    if target == 'c' or target == 'ispc':
        # Sort the struct topologically
        sorted_structs_list = topo_sort_structs(structs)

        # build ctypes structs/classes
        structs = {}
        for s in sorted_structs_list:
            structs[s.id] = type(s.id, (ctypes.Structure, ), {
                '_fields_': [(m.id, loma_to_ctypes_type(m.t, structs)) for m in s.members]
            })


        lib = CDLL(os.path.join(os.getcwd(), output_filename))
        for f in funcs.values():
            if target == 'ispc':
                # only process SIMD functions
                if not f.is_simd:
                    continue
            c_func = getattr(lib, f.id)
            argtypes = [loma_to_ctypes_type(arg, structs) for arg in f.args]
            # for simd functions, the last argument is the number of threads
            if f.is_simd:
                argtypes.append(ctypes.c_int)
            c_func.argtypes = argtypes
            c_func.restype = loma_to_ctypes_type(f.ret_type, structs)
        return structs, lib
    else:
        return module, kernels
