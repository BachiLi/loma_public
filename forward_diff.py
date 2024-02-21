import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irmutator

def forward_diff(diff_func_id : str,
                 structs : dict[str, loma_ir.Struct],
                 funcs : dict[str, loma_ir.func],
                 diff_structs : dict[str, loma_ir.Struct],
                 func : loma_ir.FunctionDef) -> loma_ir.FunctionDef:
    """ Given a primal loma function func, apply forward differentiation
        and return a function that computes the total derivative of func.

        For example, given the following function:
        def square(x : float):
            return x * x
        and let diff_func_id = 'd_square', forward_diff() should return
        def d_square(x : _dfloat):
            _return : _dfloat
            _return.val = x.val * x.val
            _return.dval = x.val * x.dval + x.dval * x.val
            return _return
        where the class _dfloat is
        class _dfloat:
            val : float
            dval : float

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

    # HW1 happens here. Modify the following IR mutators to perform
    # forward differentiation.

    # Apply the differentiation.
    class FwdDiffMutator(irmutator.IRMutator):
        def mutate_function_def(self, node):
            # HW1: TODO
            return super().mutate_function_def(node)

        def mutate_return(self, node):
            # HW1: TODO
            return super().mutate_return(node)

        def mutate_declare(self, node):
            # HW1: TODO
            return super().mutate_declare(node)

        def mutate_assign(self, node):
            # HW1: TODO
            return super().mutate_assign(node)

        def mutate_const_float(self, node):
            # HW1: TODO
            return super().mutate_const_float(node)

        def mutate_const_int(self, node):
            # HW1: TODO
            return super().mutate_const_int(node)

        def mutate_var(self, node):
            # HW1: TODO
            return super().mutate_var(node)

        def mutate_array_access(self, node):
            # HW1: TODO
            return super().mutate_array_access(node)

        def mutate_struct_access(self, node):
            # HW1: TODO
            return super().mutate_struct_access(node)

        def mutate_add(self, node):
            # HW1: TODO
            return super().mutate_add(node)

        def mutate_sub(self, node):
            # HW1: TODO
            return super().mutate_sub(node)

        def mutate_mul(self, node):
            # HW1: TODO
            return super().mutate_mul(node)

        def mutate_div(self, node):
            # HW1: TODO
            return super().mutate_div(node)

        def mutate_call(self, node):
            # HW1: TODO
            return super().mutate_call(node)

    return FwdDiffMutator().mutate_function_def(func)