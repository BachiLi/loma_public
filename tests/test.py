import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import ctypes
import error
import math

def test_declaration():
    with open('loma_code/declaration_float.py') as f:
        _, lib = compiler.compile(f.read(), '_code/declaration_float.so', 'c')
    assert abs(lib.declaration_float() - 5) < 1e-6
    with open('loma_code/declaration_int.py') as f:
        _, lib = compiler.compile(f.read(), '_code/declaration_int.so', 'c')
    assert lib.declaration_int() == 4

def test_binary_ops():
    with open('loma_code/binary_ops.py') as f:
        _, lib = compiler.compile(f.read(), '_code/binary_ops.so', 'c')
    # a = x + y = 5 + 6 = 11
    # b = a - x = 11 - 5 = 6
    # c = b * y = 6 * 6 = 36
    # d = c / a = 36 / 11
    assert abs(lib.binary_ops() - 36.0 / 11.0) < 1e-6

def test_args():
    with open('loma_code/args.py') as f:
        _, lib = compiler.compile(f.read(), '_code/args.so', 'c')
    assert lib.args(4.5, 3) == 7

def test_mutation():
    with open('loma_code/mutation.py') as f:
        _, lib = compiler.compile(f.read(), '_code/mutation.so', 'c')
    assert abs(lib.mutation() - 6) < 1e-6

def test_array_read():
    with open('loma_code/array_read.py') as f:
        _, lib = compiler.compile(f.read(), '_code/array_read.so', 'c')
    py_arr = [1.0, 2.0]
    arr = (ctypes.c_float * len(py_arr))(*py_arr)
    assert lib.array_read(arr) == 1.0

def test_array_write():
    with open('loma_code/array_write.py') as f:
        _, lib = compiler.compile(f.read(), '_code/array_write.so', 'c')
    py_arr = [0.0, 0.0]
    arr = (ctypes.c_float * len(py_arr))(*py_arr)
    lib.array_write(arr)
    assert arr[0] == 2.0

def test_compare():
    with open('loma_code/compare.py') as f:
        _, lib = compiler.compile(f.read(), '_code/compare.so', 'c')
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
        _, lib = compiler.compile(f.read(), '_code/if_else.so', 'c')
    assert lib.if_else(0.5) == 4.0
    assert lib.if_else(-0.5) == -4.0

def test_while_loop():
    with open('loma_code/while_loop.py') as f:
        _, lib = compiler.compile(f.read(), '_code/while_loop.so', 'c')
    assert lib.while_loop() == 45

def test_intrinsic_func_call():
    with open('loma_code/intrinsic_func_call.py') as f:
        _, lib = compiler.compile(f.read(), '_code/intrinsic_func_call.so', 'c')
    assert abs(lib.intrinsic_func_call() - math.sin(3.0)) < 1e-6

def test_func_decl():
    with open('loma_code/func_decl.py') as f:
        _, lib = compiler.compile(f.read(), '_code/func_decl.so', 'c')
    assert lib.func_decl() == 42

def test_struct_access():
    with open('loma_code/struct_access.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/struct_access.so', 'c')
    Foo = structs['Foo']
    foo = Foo(x=3, y=4.5)
    assert abs(lib.struct_access(foo) - 3 * 4.5 < 1e-6)

def test_struct_return():
    with open('loma_code/struct_return.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/struct_return.so', 'c')
    foo = lib.struct_return()
    assert foo.x == 5 and abs(foo.y - 3.5) < 1e-6

def test_struct_in_struct():
    with open('loma_code/struct_in_struct.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/struct_in_struct.so', 'c')
    Bar = structs['Bar']
    bar = Bar(y=4.5, z=100)
    foo = lib.struct_in_struct(bar)
    assert foo.x == 5 and abs(foo.bar.y - 4.5) < 1e-6 and foo.bar.z == 3

def test_array_in_struct():
    with open('loma_code/array_in_struct.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/array_in_struct.so', 'c')
    py_arr = [1, 2]
    arr = (ctypes.c_int * len(py_arr))(*py_arr)
    Foo = structs['Foo']
    foo = Foo(arr=arr)
    assert lib.array_in_struct(foo) == 3

def test_struct_in_array():
    with open('loma_code/struct_in_array.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/struct_in_array.so', 'c')
    Foo = structs['Foo']
    py_arr = [Foo(x=1,y=2), Foo(x=3,y=4)]
    arr = (Foo * len(py_arr))(*py_arr)
    assert lib.struct_in_array(arr) == 5

def test_struct_in_array_in_struct():
    with open('loma_code/struct_in_array_in_struct.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/struct_in_array_in_struct.so', 'c')
    Foo = structs['Foo']
    Bar = structs['Bar']
    bar_py_arr_0 = [Bar(y=2)]
    bar_arr_0 = (Bar * len(bar_py_arr_0))(*bar_py_arr_0)
    bar_py_arr_1 = [Bar(y=4)]
    bar_arr_1 = (Bar * len(bar_py_arr_1))(*bar_py_arr_1)
    foo_py_arr = [Foo(x=1,b=bar_arr_0), Foo(x=3,b=bar_arr_1)]
    foo_arr = (Foo * len(foo_py_arr))(*foo_py_arr)
    assert lib.struct_in_array_in_struct(foo_arr) == 5

def test_parallel_add():
    with open('loma_code/parallel_add.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/parallel_add.so', 'c')
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)
    lib.parallel_add(x, y, z, len(py_z))
    assert z[0] == 9 and z[1] == 14 and z[2] == 18

    with open('loma_code/parallel_add.py') as f:
        structs, lib = compiler.compile(f.read(), '_code/parallel_add.so', 'ispc')
    py_x = [2, 3, 5]
    x = (ctypes.c_int * len(py_x))(*py_x)
    py_y = [7, 11, 13]
    y = (ctypes.c_int * len(py_y))(*py_y)
    py_z = [0, 0, 0]
    z = (ctypes.c_int * len(py_z))(*py_z)
    lib.parallel_add(x, y, z, len(py_z))
    assert z[0] == 9 and z[1] == 14 and z[2] == 18

def test_duplicate_declare():
    try:
        with open('loma_code/duplicate_declare.py') as f:
            _, lib = compiler.compile(f.read(), '_code/duplicate_declare.so', 'c')
    except error.DuplicateVariable as e:
        assert e.var == 'x'
        assert e.first_lineno == 2
        assert e.duplicate_lineno == 3

def test_undeclared_var():
    try:
        with open('loma_code/undeclared_var.py') as f:
            _, lib = compiler.compile(f.read(), '_code/undeclared_var.so', 'c')
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
    test_intrinsic_func_call()
    test_func_decl()
    test_struct_access()
    test_struct_return()
    test_struct_in_struct()
    test_array_in_struct()
    test_struct_in_array()
    test_struct_in_array_in_struct()
    test_parallel_add()

    # test compile errors
    test_duplicate_declare()
    test_undeclared_var()
