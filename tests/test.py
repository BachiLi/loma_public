import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes
import error
import math
import gpuctypes.opencl as cl
import cl_utils

###########################################################################
# Correctness test

def test_declaration():
    with open('loma_code/declaration_float.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/declaration_float.so')
    assert abs(lib.declaration_float() - 5) < 1e-6
    with open('loma_code/declaration_int.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/declaration_int.so')
    assert lib.declaration_int() == 4

def test_binary_ops():
    with open('loma_code/binary_ops.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/binary_ops.so')
    # a = x + y = 5 + 6 = 11
    # b = a - x = 11 - 5 = 6
    # c = b * y = 6 * 6 = 36
    # d = c / a = 36 / 11
    assert abs(lib.binary_ops() - 36.0 / 11.0) < 1e-6

def test_args():
    with open('loma_code/args.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/args.so')
    assert lib.args(4.5, 3) == 7

def test_mutation():
    with open('loma_code/mutation.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/mutation.so')
    assert abs(lib.mutation() - 6) < 1e-6

def test_array_read():
    with open('loma_code/array_read.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/array_read.so')
    py_arr = [1.0, 2.0]
    arr = (ctypes.c_float * len(py_arr))(*py_arr)
    assert lib.array_read(arr) == 1.0

def test_array_write():
    with open('loma_code/array_write.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/array_write.so')
    py_arr = [0.0, 0.0]
    arr = (ctypes.c_float * len(py_arr))(*py_arr)
    lib.array_write(arr)
    assert arr[0] == 2.0

def test_compare():
    with open('loma_code/compare.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/compare.so')
    py_arr = [0] * 7
    arr = (ctypes.c_int * len(py_arr))(*py_arr)
    # 5 < 6 : True
    # 5 <= 6 : True
    # 5 > 6 : False
    # 5 >= 6 : False
    # 5 == 6 : False
    lib.compare(5, 6, arr)
    assert arr[0] != 0
    assert arr[1] != 0
    assert arr[2] == 0
    assert arr[3] == 0
    assert arr[4] == 0
    assert arr[5] == 0
    assert arr[6] != 0
    # 5 < 5 : False
    # 5 <= 5 : True
    # 5 > 5 : False
    # 5 >= 5 : True
    # 5 == 5 : True
    lib.compare(5, 5, arr)
    assert arr[0] == 0
    assert arr[1] != 0
    assert arr[2] == 0
    assert arr[3] != 0
    assert arr[4] != 0
    assert arr[5] == 0
    assert arr[6] == 0

def test_if_else():
    with open('loma_code/if_else.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/if_else.so')
    assert lib.if_else(0.5) == 4.0
    assert lib.if_else(-0.5) == -4.0

def test_while_loop():
    with open('loma_code/while_loop.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/while_loop.so')
    assert lib.while_loop() == 45

def test_local_static_array():
    with open('loma_code/local_static_array.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/local_static_array.so')
    assert lib.local_static_array() == 55

def test_local_array_init_zero():
    with open('loma_code/local_array_init_zero.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/local_array_init_zero.so')
    assert lib.local_array_init_zero() == 13

def test_intrinsic_func_call():
    with open('loma_code/intrinsic_func_call.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/intrinsic_func_call.so')
    assert abs(lib.intrinsic_func_call() - math.sin(3.0)) < 1e-6

def test_func_decl():
    with open('loma_code/func_decl.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/func_decl.so')
    assert lib.func_decl() == 42

def test_struct_access():
    with open('loma_code/struct_access.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/struct_access.so')
    Foo = structs['Foo']
    foo = Foo(x=3, y=4.5)
    assert abs(lib.struct_access(foo) - 3 * 4.5 < 1e-6)

def test_struct_return():
    with open('loma_code/struct_return.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/struct_return.so')
    foo = lib.struct_return()
    assert foo.x == 5 and abs(foo.y - 3.5) < 1e-6

def test_struct_in_struct():
    with open('loma_code/struct_in_struct.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/struct_in_struct.so')
    Bar = structs['Bar']
    bar = Bar(y=4.5, z=100)
    foo = lib.struct_in_struct(bar)
    assert foo.x == 5 and abs(foo.bar.y - 4.5) < 1e-6 and foo.bar.z == 3

def test_array_in_struct():
    with open('loma_code/array_in_struct.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/array_in_struct.so')
    py_arr = [1, 2]
    arr = (ctypes.c_int * len(py_arr))(*py_arr)
    Foo = structs['Foo']
    foo = Foo(arr=arr)
    assert lib.array_in_struct(foo) == 3

def test_struct_in_array():
    with open('loma_code/struct_in_array.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/struct_in_array.so')
    Foo = structs['Foo']
    py_arr = [Foo(x=1,y=2), Foo(x=3,y=4)]
    arr = (Foo * len(py_arr))(*py_arr)
    assert lib.struct_in_array(arr) == 5

def test_struct_in_array_in_struct():
    with open('loma_code/struct_in_array_in_struct.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/struct_in_array_in_struct.so')
    Foo = structs['Foo']
    Bar = structs['Bar']
    bar_py_arr_0 = [Bar(y=2)]
    bar_arr_0 = (Bar * len(bar_py_arr_0))(*bar_py_arr_0)
    bar_py_arr_1 = [Bar(y=4)]
    bar_arr_1 = (Bar * len(bar_py_arr_1))(*bar_py_arr_1)
    foo_py_arr = [Foo(x=1,b=bar_arr_0), Foo(x=3,b=bar_arr_1)]
    foo_arr = (Foo * len(foo_py_arr))(*foo_py_arr)
    assert lib.struct_in_array_in_struct(foo_arr) == 5

def test_struct_init_zero():
    with open('loma_code/struct_init_zero.py') as f:
        _, lib = compiler.compile(f.read(),
                                  target = 'c',
                                  output_filename = '_code/struct_init_zero.so')
    assert lib.struct_init_zero() == 0

def test_parallel_add():
    with open('loma_code/parallel_add.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/parallel_add.so')
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)
    lib.parallel_add(x, y, z, len(py_z))
    assert z[0] == 9 and z[1] == 14 and z[2] == 18

    with open('loma_code/parallel_add.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'ispc',
                                        output_filename = '_code/parallel_add.so')
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)
    lib.parallel_add(x, y, z, len(py_z))
    assert z[0] == 9 and z[1] == 14 and z[2] == 18

    cl_ctx, cl_device, cl_cmd_queue = cl_utils.create_context()

    with open('loma_code/parallel_add.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'opencl',
                                        opencl_context = cl_ctx,
                                        opencl_device = cl_device,
                                        opencl_command_queue = cl_cmd_queue)
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)

    status = ctypes.c_int32()
    bufx = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_READ_ONLY | cl.CL_MEM_COPY_HOST_PTR,
                             ctypes.sizeof(x),
                             ctypes.byref(x),
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)
    bufy = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_READ_ONLY | cl.CL_MEM_COPY_HOST_PTR,
                             ctypes.sizeof(y),
                             ctypes.byref(y),
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)
    bufz = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_WRITE_ONLY,
                             ctypes.sizeof(z),
                             None,
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)

    lib.parallel_add(bufx, bufy, bufz, len(py_z))
    cl.clFinish(cl_cmd_queue)

    cl.clEnqueueReadBuffer(cl_cmd_queue,
                           bufz,
                           cl.CL_TRUE,
                           0,
                           ctypes.sizeof(z),
                           ctypes.byref(z),
                           0,
                           None,
                           None)

    assert z[0] == 9 and z[1] == 14 and z[2] == 18

def test_simd_local_func():
    with open('loma_code/simd_local_func.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'c',
                                        output_filename = '_code/simd_local_func.so')
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)
    lib.simd_local_func(x, y, z, len(py_z))
    assert z[0] == 9 and z[1] == 14 and z[2] == 18

    with open('loma_code/simd_local_func.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'ispc',
                                        output_filename = '_code/simd_local_func.so')
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)
    lib.simd_local_func(x, y, z, len(py_z))
    assert z[0] == 9 and z[1] == 14 and z[2] == 18

    cl_ctx, cl_device, cl_cmd_queue = cl_utils.create_context()

    with open('loma_code/simd_local_func.py') as f:
        structs, lib = compiler.compile(f.read(),
                                        target = 'opencl',
                                        opencl_context = cl_ctx,
                                        opencl_device = cl_device,
                                        opencl_command_queue = cl_cmd_queue)
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)

    status = ctypes.c_int32()
    bufx = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_READ_ONLY | cl.CL_MEM_COPY_HOST_PTR,
                             ctypes.sizeof(x),
                             ctypes.byref(x),
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)
    bufy = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_READ_ONLY | cl.CL_MEM_COPY_HOST_PTR,
                             ctypes.sizeof(y),
                             ctypes.byref(y),
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)
    bufz = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_WRITE_ONLY,
                             ctypes.sizeof(z),
                             None,
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)

    lib.simd_local_func(bufx, bufy, bufz, len(py_z))
    cl.clFinish(cl_cmd_queue)

    cl.clEnqueueReadBuffer(cl_cmd_queue,
                           bufz,
                           cl.CL_TRUE,
                           0,
                           ctypes.sizeof(z),
                           ctypes.byref(z),
                           0,
                           None,
                           None)

    assert z[0] == 9 and z[1] == 14 and z[2] == 18

###########################################################################
# Test compile error

def test_duplicate_declare():
    try:
        with open('loma_code/duplicate_declare.py') as f:
            _, lib = compiler.compile(f.read(),
                                      target = 'c',
                                      output_filename = '_code/duplicate_declare.so')
    except error.DuplicateVariable as e:
        assert e.var == 'x'
        assert e.first_lineno == 2
        assert e.duplicate_lineno == 3

def test_undeclared_var():
    try:
        with open('loma_code/undeclared_var.py') as f:
            _, lib = compiler.compile(f.read(),
                                      target = 'c',
                                      output_filename = '_code/undeclared_var.so')
    except error.UndeclaredVariable as e:
        assert e.var == 'b'
        assert e.lineno == 3

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    test_declaration()
    test_binary_ops()
    test_args()
    test_mutation()
    test_array_read()
    test_array_write()
    test_compare()
    test_if_else()
    test_while_loop()
    test_local_static_array()
    test_local_array_init_zero()
    test_intrinsic_func_call()
    test_func_decl()
    test_struct_access()
    test_struct_return()
    test_struct_in_struct()
    test_array_in_struct()
    test_struct_in_array()
    test_struct_in_array_in_struct()
    test_struct_init_zero()
    test_parallel_add()
    test_simd_local_func()

    # test compile errors
    test_duplicate_declare()
    test_undeclared_var()
