import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent)
import compiler
import ctypes
import error
import math
import slang_utils
import slangpy
import unittest
import numpy as np
import random

epsilon = 1e-4

class Homework3Test(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def test_ifelse_fwd(self):
        with open('loma_code/ifelse_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.4)
        y = _dfloat(1, 0.5)
        z = lib.fwd_ifelse(x, y)
        assert abs(z.val - 5 * x.val) < epsilon and \
            abs(z.dval - 5 * x.dval) < epsilon

        # test both branches
        x = _dfloat(1.23, 0.4)
        y = _dfloat(-1, 0.5)
        z = lib.fwd_ifelse(x, y)
        assert abs(z.val - 2 * x.val) < epsilon and \
            abs(z.dval - 2 * x.dval) < epsilon

    def test_ifelse_rev(self):
        with open('loma_code/ifelse_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_rev')
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 5 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

        # test both branches
        x = 1.23
        _dx = ctypes.c_float(0)
        y = -1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 2 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

    def test_ifelse_side_effects_rev(self):
        with open('loma_code/ifelse_side_effects_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/ifelse_side_effects_rev')
        
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse_side_effects(x, _dx, y, _dy, 0.3)

        assert abs(_dx.value - 0.3 * math.cos(5.0 * x) * 5) < epsilon and \
            abs(_dy.value) < epsilon

        # test both branches
        x = 1.23
        _dx = ctypes.c_float(0)
        y = -1.0
        _dy = ctypes.c_float(0)
        lib.rev_ifelse_side_effects(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 2 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

    def test_nested_ifelse_rev(self):
        with open('loma_code/nested_ifelse_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_ifelse_rev')
        
        # test all three branches
        x = 1.23
        _dx = ctypes.c_float(0)
        y = 1
        _dy = ctypes.c_float(0)
        lib.rev_nested_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 0.3 * math.cos(5.0 * x) * 5) < epsilon and \
            abs(_dy.value) < epsilon

        x = -1.23
        _dx = ctypes.c_float(0)
        y = 1
        _dy = ctypes.c_float(0)
        lib.rev_nested_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value + 0.3 * math.sin(5.0 * x) * 5) < epsilon and \
            abs(_dy.value) < epsilon

        x = 1.23
        _dx = ctypes.c_float(0)
        y = -1
        _dy = ctypes.c_float(0)
        lib.rev_nested_ifelse(x, _dx, y, _dy, 0.3)
        assert abs(_dx.value - 2 * 0.3) < epsilon and \
            abs(_dy.value) < epsilon

    def test_func_call_fwd(self):
        with open('loma_code/func_call_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        y = _dfloat(0.5, 0.5)
        z = lib.fwd_func_call(x, y)
        # z = 2 * (x * x * y + y * y)
        # dz = 2 * (2 * dx * x * y + x * x * dy + 2 * dy * y)
        assert abs(z.val - 2 * (x.val * x.val * y.val + y.val * y.val)) < epsilon and \
            abs(z.dval - 2 * (2 * x.dval * x.val * y.val + x.val * x.val * y.dval + 2 * y.dval * y.val)) < epsilon

    def test_chained_calls_fwd(self):
        with open('loma_code/chained_calls_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/chained_calls_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        out = lib.fwd_chained_calls(x)

        # out = sin(2 * x * x)
        # dout = dx * cos(2 * x * x) * 4 * x 
        assert abs(out.dval - (x.dval * math.cos(2 * x.val * x.val) * 4 * x.val)) < epsilon

    def test_call_stmt_fwd(self):
        with open('loma_code/call_stmt_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(0.67, 0.4)
        z = lib.fwd_call_stmt(x)
        # z = 2 * (x * x + x)
        # dout = 2 * dx * (2 * x + 1)
        assert abs(z.dval - (2 * x.dval * (2 * x.val + 1))) < epsilon

    def test_func_call_rev(self):
        with open('loma_code/func_call_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.5
        _dy = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_func_call(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z = 2 * (x * x * y + y * y)
        # dx = 4 * x * y * dout
        # dy = 2 * x^2 * dout + 2 * y * dout
        assert abs(_dx.value - (4 * x * y * dout)) < epsilon and \
            abs(_dy.value - dout * (2 * x * x + 2 * y))

    def test_func_call_rev2(self):
        with open('loma_code/func_call_rev2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_rev2')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.5
        _dy = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_func_call(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z = 2 * ((x + y) * (x * y))
        # dx = 2 * dout * ((x * y) + (x + y) * y)
        # dy = 2 * dout * ((x * y) + (x + y) * x)
        assert abs(_dx.value - (2 * dout * ((x * y) + (x + y) * y))) < epsilon and \
            abs(_dy.value - (2 * dout * ((x * y) + (x + y) * x))) < epsilon

    def test_func_call_assign_rev(self):
        with open('loma_code/func_call_assign_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/func_call_assign_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.5
        _dy = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_func_call_assign(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)
        # z = 2 * x * x * y * y
        # dx = dout * 4 * x * y^2
        # dy = dout * 4 * x^2 * y
        assert abs(_dx.value - dout * 4 * x * y * y) < epsilon and \
            abs(_dy.value - dout * 4 * x * x * y) < epsilon

    def test_call_array_rev(self):
        with open('loma_code/call_array_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_array_rev')
        x = ctypes.c_float(0)
        _dx = ctypes.c_float(0)
        _dout = 0.3
        z = lib.rev_call_array(ctypes.pointer(x),
                               ctypes.pointer(_dx),
                               _dout)
        # y = (x * x + x)
        # dx = dy * (2 * x + 1)
        assert abs(_dx.value - (_dout * (2 * x.value + 1))) < epsilon

    def test_call_stmt_rev(self):
        with open('loma_code/call_stmt_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_call_stmt(x, ctypes.byref(_dx), dout)
        # y = 2 * (x * x + x)
        # dx = 2 * dout * (2 * x + 1)
        assert abs(_dx.value - (2 * dout * (2 * x + 1))) < epsilon

    def test_call_stmt2_rev(self):
        with open('loma_code/call_stmt2_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt2_rev')
        x = 0.67
        _dx = ctypes.c_float(0)
        _dy = 0.3
        z = lib.rev_call_stmt2(x, ctypes.byref(_dx), _dy)
        # y = (x * x + x)
        # dx = dy * (2 * x + 1)
        assert abs(_dx.value - (_dy * (2 * x + 1))) < epsilon

    def test_call_stmt_side_effects(self):
        with open('loma_code/call_stmt_side_effects.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_side_effects')
        x = 0.67
        _dx = ctypes.c_float(0)
        dout = 0.3
        z = lib.rev_call_stmt_side_effects(x, ctypes.byref(_dx), dout)
        # y = 2 * (x * x + x) + 10 * x
        # dx = dout * (2 * (2 * x + 1) + 10)
        assert abs(_dx.value - (dout * (2 * (2 * x + 1) + 10))) < epsilon

    def test_call_stmt_side_effects2(self):
        with open('loma_code/call_stmt_side_effects2.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_side_effects2')
        x = 0.67
        _dx = ctypes.c_float(0)
        y = 0.89
        _dy = ctypes.c_float(0)
        dout = 0.3
        out = lib.rev_call_stmt_side_effects2(x, ctypes.byref(_dx), y, ctypes.byref(_dy), dout)

        # out = 2 * (x * x + x) + (0.5 * y)^2 * x
        # dx = dout * (2 * (2 * x + 1) + (0.5 * y)^2)
        # dy = dout * (0.5 * y) * x
        assert abs(_dx.value - (dout * (2 * (2 * x + 1) + 0.25 * y * y))) < epsilon and \
            abs(_dy.value - (dout * (0.5 * y * x))) < epsilon

    def test_call_stmt_array_rev(self):
        with open('loma_code/call_stmt_array_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/call_stmt_array_rev')
        x = ctypes.c_float(0)
        _dx = ctypes.c_float(0)
        _dy = ctypes.c_float(0.3)
        z = lib.rev_call_stmt_array(ctypes.pointer(x),
                                    ctypes.pointer(_dx),
                                    ctypes.pointer(_dy))
        # y = (x * x + x)
        # dx = dy * (2 * x + 1)
        assert abs(_dx.value - (_dy.value * (2 * x.value + 1))) < epsilon

    def test_chained_calls_rev(self):
        with open('loma_code/chained_calls_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/chained_calls')
        x = 0.67
        _dx = ctypes.c_float(0)
        dout = 0.3
        out = lib.rev_chained_calls(x, ctypes.byref(_dx), dout)

        # out = sin(2 * x * x)
        # dx = dout * cos(2 * x * x) * 4 * x 
        assert abs(_dx.value - (dout * math.cos(2 * x * x) * 4 * x)) < epsilon

    def test_while_loop_fwd(self):
        with open('loma_code/while_loop_fwd.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/while_loop_fwd')
        _dfloat = structs['_dfloat']
        x = _dfloat(1.23, 0.4)
        n = 5
        out = lib.fwd_while_loop(x, n)

        # out = sin(sin(sin(sin(sin(x)))))
        # dout = dx * (cos(sin(sin(sin(sin(x))))) *
        #              cos(sin(sin(sin(x)))) *
        #              cos(sin(sin(x))) *
        #              cos(sin(x)) *
        #              cos(x))
        assert abs(out.dval - x.dval * (math.cos(math.sin(math.sin(math.sin(math.sin(x.val))))) * \
                                        math.cos(math.sin(math.sin(math.sin(x.val))))) * \
                                        math.cos(math.sin(math.sin(x.val))) * \
                                        math.cos(math.sin(x.val)) * \
                                        math.cos(x.val)) < epsilon

    def test_while_loop_rev(self):
        with open('loma_code/while_loop_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/while_loop_rev')
        x = 1.23
        _dx = ctypes.c_float(0)
        n = 5
        _dn = ctypes.c_int(0)
        dout = 0.4
        out = lib.rev_while_loop(x, _dx, n, _dn, dout)

        # out = sin(sin(sin(sin(sin(x)))))
        # dx = dout * (cos(sin(sin(sin(sin(x))))) *
        #              cos(sin(sin(sin(x)))) *
        #              cos(sin(sin(x))) *
        #              cos(sin(x)) *
        #              cos(x))
        assert abs(_dx.value - dout * (math.cos(math.sin(math.sin(math.sin(math.sin(x))))) * \
                                       math.cos(math.sin(math.sin(math.sin(x))))) * \
                                       math.cos(math.sin(math.sin(x))) * \
                                       math.cos(math.sin(x)) * \
                                       math.cos(x)) < epsilon

    def test_nested_while_loop_rev(self):
        with open('loma_code/nested_while_loop_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/nested_while_loop_rev')
        x = 1.23
        _dx = ctypes.c_float(0)
        n = 5
        _dn = ctypes.c_int(0)
        dout = 0.4
        lib.rev_nested_while_loop(x, _dx, n, _dn, dout)

        # out = x + (n * (n-1)) * x^2
        # dx = dout * (1 + x * (n * (n - 1)))
        assert abs(_dx.value - dout * (x * (n * (n - 1)))) < epsilon

    def test_three_level_while_loop_rev(self):
        with open('loma_code/three_level_while_loop_rev.py') as f:
            structs, lib = compiler.compile(f.read(),
                                            target = 'c',
                                            output_filename = '_code/three_level_while_loop_rev')
        x = 0.123
        _dx = ctypes.c_float(0)
        n = 5
        _dn = ctypes.c_int(0)
        dout = 0.4
        lib.rev_three_level_while_loop(x, _dx, n, _dn, dout)

        # out = x + n^3 * x^2
        # dx = dout * (1 + 2 * x * n^3))
        assert abs(_dx.value - dout * (1 + 2 * x * n * n * n)) < epsilon

    def test_parallel_copy(self):
        slang_device = slang_utils.create_slang_device()
        with open('loma_code/parallel_copy.py') as f:
            module, kernels = compiler.compile(f.read(),
                                               target = 'slang',
                                               slang_device = slang_device)
        x = module._dfloat(0.123, 0.456)
        n = 10000

        buffer_z = slangpy.Tensor.empty(
            device=slang_device,
            dtype=module._dfloat,
            shape=(n,)
        )

        cursor_z = buffer_z.cursor()
        for i in range(n):
            cursor_z[i].write({'val':0.0, 'dval':0.0})
        cursor_z.apply()

        kernels['fwd_parallel_copy'].dispatch(\
            thread_count=[n, 1, 1],
            _total_threads=n,
            x=x,
            z=buffer_z.storage)

        cursor_z = buffer_z.cursor()
        for i in range(n):
            assert abs(cursor_z[i].read()['dval'] - x['dval']) < epsilon

        layout = kernels['rev_parallel_copy'].program.layout
        f = layout.find_function_by_name('rev_parallel_copy')
        
        n = 10000
        x = 0.123
        buffer_dx = slangpy.Tensor.empty(
            device=slang_device,
            dtype=float,
            shape=(1,)
        )
        cursor_dx = buffer_dx.cursor()
        cursor_dx[0].write(0.0)
        cursor_dx.apply()
        buffer_dz = slangpy.Tensor.empty(
            device=slang_device,
            dtype=float,
            shape=(n,)
        )
        cursor_dz = buffer_dz.cursor()
        for i in range(n):
            cursor_dz[i].write(0.456 / n)
        cursor_dz.apply()

        # f.parameters[0].name == '_tid'
        # f.parameters[1].name == '_total_threads'
        kernels['rev_parallel_copy'].dispatch(**{\
            'thread_count':[n, 1, 1],
            f.parameters[1].name:n,
            f.parameters[2].name:x,
            f.parameters[3].name:buffer_dx.storage,
            f.parameters[4].name:buffer_dz.storage})
        cursor_dx = buffer_dx.cursor()
        assert abs(cursor_dx[0].read() - 0.456) < epsilon

    def test_parallel_add(self):
        slang_device = slang_utils.create_slang_device()
        with open('loma_code/parallel_add.py') as f:
            module, kernels = compiler.compile(f.read(),
                                               target = 'slang',
                                               slang_device = slang_device)

        n = 10000
        buffer_x = slangpy.Tensor.empty(
            device=slang_device,
            dtype=module._dfloat,
            shape=(n,)
        )
        buffer_y = slangpy.Tensor.empty(
            device=slang_device,
            dtype=module._dfloat,
            shape=(n,)
        )
        buffer_z = slangpy.Tensor.empty(
            device=slang_device,
            dtype=module._dfloat,
            shape=(n,)
        )
        cursor_x = buffer_x.cursor()
        cursor_y = buffer_y.cursor()
        cursor_z = buffer_z.cursor()
        for i in range(n):
            cursor_x[i].write({'val':random.random(),
                               'dval':random.random()})
            cursor_y[i].write({'val':random.random(),
                               'dval':random.random()})
            cursor_z[i].write({'val':0.0, 'dval':0.0})
        cursor_x.apply()
        cursor_y.apply()
        cursor_z.apply()

        kernels['fwd_parallel_add'].dispatch(\
            thread_count=[n, 1, 1],
            _total_threads=n,
            x=buffer_x.storage,
            y=buffer_y.storage,
            z=buffer_z.storage)
        cursor_z = buffer_z.cursor()
        for i in range(n):
            assert abs(cursor_z[i].read()['dval'] - \
                       (cursor_x[i].read()['dval'] + \
                        cursor_y[i].read()['dval'])) < epsilon

        n = 10000
        buffer_x = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.random.rand(n).astype(np.float32)
        )
        buffer_dx = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.zeros([n], dtype=np.float32)
        )
        buffer_y = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.random.rand(n).astype(np.float32)
        )
        buffer_dy = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.zeros([n], dtype=np.float32)
        )
        buffer_dz = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.random.rand(n).astype(np.float32)
        )

        layout = kernels['rev_parallel_add'].program.layout
        f = layout.find_function_by_name('rev_parallel_add')

        # f.parameters[0].name == '_tid'
        # f.parameters[1].name == '_total_threads'
        kernels['rev_parallel_add'].dispatch(**{\
            'thread_count':[n, 1, 1],
            f.parameters[1].name:n,
            f.parameters[2].name:buffer_x.storage,
            f.parameters[3].name:buffer_dx.storage,
            f.parameters[4].name:buffer_y.storage,
            f.parameters[5].name:buffer_dy.storage,
            f.parameters[6].name:buffer_dz.storage})
        cursor_dx = buffer_dx.cursor()
        cursor_dy = buffer_dy.cursor()
        cursor_dz = buffer_dz.cursor()
        for i in range(n):
            assert abs(cursor_dx[i].read() - cursor_dz[i].read()) < epsilon
            assert abs(cursor_dy[i].read() - cursor_dz[i].read()) < epsilon

    def test_parallel_reduce(self):
        slang_device = slang_utils.create_slang_device()
        with open('loma_code/parallel_reduce.py') as f:
            module, kernels = compiler.compile(f.read(),
                                               target = 'slang',
                                               slang_device = slang_device)

        n = 10000
        buffer_x = slangpy.Tensor.empty(
            device=slang_device,
            dtype=module._dfloat,
            shape=(n,)
        )
        buffer_z = slangpy.Tensor.empty(
            device=slang_device,
            dtype=module._dfloat,
            shape=(1,)
        )
        cursor_x = buffer_x.cursor()
        cursor_z = buffer_z.cursor()
        dval_sum = 0.0
        for i in range(n):
            val = random.random() / n
            dval = random.random() / n
            cursor_x[i].write({'val':val, 'dval':dval})
            dval_sum += dval
        cursor_z[0].write({'val':0.0, 'dval':0.0})
        cursor_x.apply()
        cursor_z.apply()

        kernels['fwd_parallel_reduce'].dispatch(\
            thread_count=[n, 1, 1],
            _total_threads=n,
            x=buffer_x.storage,
            z=buffer_z.storage)
        cursor_z = buffer_z.cursor()
        assert abs(cursor_z[0].read()['dval'] - dval_sum) < epsilon

        n = 10000
        buffer_x = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.random.rand(n).astype(np.float32)
        )
        buffer_dx = slangpy.Tensor.from_numpy(
            device=slang_device,
            ndarray=np.zeros([n], dtype=np.float32)
        )
        dz = random.random()

        layout = kernels['rev_parallel_reduce'].program.layout
        f = layout.find_function_by_name('rev_parallel_reduce')

        # f.parameters[0].name == '_tid'
        # f.parameters[1].name == '_total_threads'
        kernels['rev_parallel_reduce'].dispatch(**{\
            'thread_count':[n, 1, 1],
            f.parameters[1].name:n,
            f.parameters[2].name:buffer_x.storage,
            f.parameters[3].name:buffer_dx.storage,
            f.parameters[4].name:dz})
        cursor_dx = buffer_dx.cursor()
        for i in range(n):
            assert abs(cursor_dx[i].read() - dz) < epsilon

if __name__ == '__main__':
    unittest.main()
