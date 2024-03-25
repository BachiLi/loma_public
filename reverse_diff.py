import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irmutator
import autodiff
import string
import random

# From https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
def random_id_generator(size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def reverse_diff(diff_func_id : str,
                 structs : dict[str, loma_ir.Struct],
                 funcs : dict[str, loma_ir.func],
                 diff_structs : dict[str, loma_ir.Struct],
                 func : loma_ir.FunctionDef) -> loma_ir.FunctionDef:
    """ Given a primal loma function func, apply reverse differentiation
        and return a function that computes the total derivative of func.

        For example, given the following function:
        def square(x : In[float]) -> float:
            return x * x
        and let diff_func_id = 'd_square', reverse_diff() should return
        def d_square(x : In[float], _dx : Out[float], _dreturn : float):
            _dx = _dx + _dreturn * x + _dreturn * x

        Parameters:
        diff_func_id - the ID of the returned function
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
        diff_structs - a dictionary that maps the ID of the primal
                Struct to the corresponding differential Struct
                e.g., diff_structs['float'] returns _dfloat
        func - the function to be differentiated
    """

    def merge_dicts(x, y):
        for key, y_value in y.items():
            if key in x:
                x_value = x[key]
                x[key] = loma_ir.BinaryOp(\
                    loma_ir.Add(),
                    x_value,
                    y_value,
                    lineno = x_value.lineno,
                    t = x_value.t)
            else:
                x[key] = y_value
        return x

    def type_to_string(t):
        match t:
            case loma_ir.Int():
                return 'int'
            case loma_ir.Float():
                return 'float'
            case loma_ir.Array():
                return 'array_' + type_to_string(t.t)
            case loma_ir.Struct():
                return t.id
            case _:
                assert False

    def assign_zero(target):
        match target.t:
            case loma_ir.Int():
                return []
            case loma_ir.Float():
                return [loma_ir.Assign(target, loma_ir.ConstFloat(0.0))]
            case loma_ir.Struct():
                s = target.t
                stmts = []
                for m in s.members:
                    target_m = loma_ir.StructAccess(
                        target, m.id, t = m.t)
                    if isinstance(m.t, loma_ir.Float):
                        stmts += assign_zero(target_m)
                    elif isinstance(m.t, loma_ir.Int):
                        pass
                    elif isinstance(m.t, loma_ir.Struct):
                        stmts += assign_zero(target_m)
                    else:
                        assert isinstance(m.t, loma_ir.Array)
                        assert m.t.static_size is not None
                        for i in range(m.t.static_size):
                            target_m = loma_ir.ArrayAccess(
                                target_m, loma_ir.ConstInt(i), t = m.t.t)
                            stmts += assign_zero(target_m)
                return stmts
            case _:
                assert False

    def accum_deriv(target, deriv):
        match target.t:
            case loma_ir.Int():
                return []
            case loma_ir.Float():
                return [loma_ir.Assign(target,
                    loma_ir.BinaryOp(loma_ir.Add(), target, deriv))]
            case loma_ir.Struct():
                s = target.t
                stmts = []
                for m in s.members:
                    target_m = loma_ir.StructAccess(
                        target, m.id, t = m.t)
                    deriv_m = loma_ir.StructAccess(
                        deriv, m.id, t = m.t)
                    if isinstance(m.t, loma_ir.Float):
                        stmts += accum_deriv(target_m, deriv_m)
                    elif isinstance(m.t, loma_ir.Int):
                        pass
                    elif isinstance(m.t, loma_ir.Struct):
                        stmts += accum_deriv(target_m, deriv_m)
                    else:
                        assert isinstance(m.t, loma_ir.Array)
                        assert m.t.static_size is not None
                        for i in range(m.t.static_size):
                            target_m = loma_ir.ArrayAccess(
                                target_m, loma_ir.ConstInt(i), t = m.t.t)
                            deriv_m = loma_ir.ArrayAccess(
                                deriv_m, loma_ir.ConstInt(i), t = m.t.t)
                            stmts += assign_zero(deriv_m)
                return stmts
            case _:
                assert False

    # HW2 happens here. Modify the following IR mutators to perform
    # reverse differentiation.

    # Apply the differentiation.
    class RevDiffMutator(irmutator.IRMutator):
        def mutate_function_def(self, node):
            # HW2: TODO
            return super().mutate_function_def(node)

        def mutate_return(self, node):
            # HW2: TODO
            return super().mutate_return(node)

        def mutate_declare(self, node):
            # HW2: TODO
            return super().mutate_declare(node)

        def mutate_assign(self, node):
            # HW2: TODO
            return super().mutate_assign(node)

        def mutate_const_float(self, node):
            # HW2: TODO
            return super().mutate_const_float(node)

        def mutate_const_int(self, node):
            # HW2: TODO
            return super().mutate_const_int(node)

        def mutate_var(self, node):
            # HW2: TODO
            return super().mutate_var(node)

        def mutate_array_access(self, node):
            # HW2: TODO
            return super().mutate_array_access(node)

        def mutate_struct_access(self, node):
            # HW2: TODO
            return super().mutate_struct_access(node)

        def mutate_add(self, node):
            # HW2: TODO
            return super().mutate_add(node)

        def mutate_sub(self, node):
            # HW2: TODO
            return super().mutate_sub(node)

        def mutate_mul(self, node):
            # HW2: TODO
            return super().mutate_mul(node)

        def mutate_div(self, node):
            # HW2: TODO
            return super().mutate_div(node)

        def mutate_call(self, node):
            # HW2: TODO
            return super().mutate_call(node)

    return RevDiffMutator().mutate_function_def(func)
