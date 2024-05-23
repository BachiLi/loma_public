import ir

ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irmutator
import autodiff
from itertools import chain


def forward_diff(
    diff_func_id: str,
    structs: dict[str, loma_ir.Struct],
    funcs: dict[str, loma_ir.func],
    diff_structs: dict[str, loma_ir.Struct],
    func: loma_ir.FunctionDef,
    func_to_fwd: dict[str, str],
) -> loma_ir.FunctionDef:
    """Given a primal loma function func, apply forward differentiation
    and return a function that computes the total derivative of func.

    For example, given the following function:
    def square(x : In[float]) -> float:
        return x * x
    and let diff_func_id = 'd_square', forward_diff() should return
    def d_square(x : In[_dfloat]) -> _dfloat:
        return make__dfloat(x.val * x.val, x.val * x.dval + x.dval * x.val)
    where the class _dfloat is
    class _dfloat:
        val : float
        dval : float
    and the function make__dfloat is
    def make__dfloat(val : In[float], dval : In[float]) -> _dfloat:
        ret : _dfloat
        ret.val = val
        ret.dval = dval
        return ret

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
    func_to_fwd - mapping from primal function ID to its forward differentiation
    """

    # HW1 happens here. Modify the following IR mutators to perform
    # forward differentiation.

    # Apply the differentiation.
    class FwdDiffMutator(irmutator.IRMutator):

        def mutate_function_def(self, node):
            # Arguments
            dargs = []
            for arg in node.args:
                dstructs_t = autodiff.type_to_diff_type(diff_structs, arg.t)
                darg = loma_ir.Arg(id=arg.id, t=dstructs_t, i=arg.i)
                dargs.append(darg)

            # Return
            return_dstruct = autodiff.type_to_diff_type(diff_structs, node.ret_type)

            # Body
            new_body = [self.mutate_stmt(stmt) for stmt in node.body]
            # Important: mutate_stmt can return a list of statements. We need to flatten the list.
            new_body = irmutator.flatten(new_body)

            return loma_ir.FunctionDef(
                diff_func_id,
                dargs,
                new_body,
                node.is_simd,
                node.is_openMpi,
                return_dstruct,
                lineno=node.lineno,
            )

            # return super().mutate_function_def(node)

        def mutate_return(self, node):

            mutated_node = self.mutate_expr(node.val)

            if node.val.t == loma_ir.Int():
                return loma_ir.Return(mutated_node[0], lineno=node.lineno)
            elif isinstance(node.val.t, loma_ir.Struct):
                return node
            else:
                return loma_ir.Return(
                    loma_ir.Call("make__dfloat", [mutated_node[0], mutated_node[1]]),
                    lineno=node.lineno,
                )

        def mutate_declare(self, node):
            mutated_expression = None
            if node.val:
                mutated_expression = self.mutate_expr(node.val)

                if isinstance(mutated_expression, list) and (mutated_expression[0], loma_ir.Call):
                    mutated_expression = mutated_expression[0]
                elif isinstance(node.t, loma_ir.Int):
                    mutated_expression = mutated_expression[0]
                elif isinstance(node.t, loma_ir.Float):
                    mutated_expression = loma_ir.Call(
                        "make__dfloat", [mutated_expression[0], mutated_expression[1]]
                    )

            declare_dstruct = autodiff.type_to_diff_type(diff_structs, node.t)

            return loma_ir.Declare(
                node.target, declare_dstruct, mutated_expression, lineno=node.lineno
            )

        def mutate_assign(self, node):
            mutated_expression = None
            if node.val:
                mutated_expression = self.mutate_expr(node.val)

                if isinstance(node.val.t, loma_ir.Int):
                    mutated_expression = mutated_expression[0]
                elif isinstance(node.val.t, loma_ir.Float):
                    mutated_expression = loma_ir.Call(
                        "make__dfloat", [mutated_expression[0], mutated_expression[1]]
                    )
            # Parse expressions in target and get the val
            if isinstance(node.target, loma_ir.StructAccess):
                mutated_target = loma_ir.StructAccess(
                    node.target.struct, node.target.member_id
                )
            elif isinstance(node.target.t, loma_ir.Struct):
                mutated_target = self.mutate_expr(node.target)
            else:
                temp = self.mutate_expr(node.target)
                if isinstance(temp[0], loma_ir.StructAccess):
                    mutated_target = temp[0].struct
                else:
                    mutated_target = temp[0]

            return loma_ir.Assign(
                mutated_target, mutated_expression, lineno=node.lineno
            )

        def mutate_ifelse(self, node):
            new_cond, _ = self.mutate_expr(node.cond)
            new_then_stmts = [self.mutate_stmt(stmt) for stmt in node.then_stmts]
            new_else_stmts = [self.mutate_stmt(stmt) for stmt in node.else_stmts]
            # Important: mutate_stmt can return a list of statements. We need to flatten the lists.
            new_then_stmts = irmutator.flatten(new_then_stmts)
            new_else_stmts = irmutator.flatten(new_else_stmts)
            return loma_ir.IfElse(\
                new_cond,
                new_then_stmts,
                new_else_stmts,
                lineno = node.lineno)

        def mutate_while(self, node):
            new_cond, _ = self.mutate_expr(node.cond)
            new_body = [self.mutate_stmt(stmt) for stmt in node.body]
            # Important: mutate_stmt can return a list of statements. We need to flatten the list.
            new_body = irmutator.flatten(new_body)
            return loma_ir.While(\
                new_cond,
                node.max_iter,
                new_body,
                lineno = node.lineno)

        def mutate_const_float(self, node):
            return (node, loma_ir.ConstFloat(0.0))

        def mutate_const_int(self, node):
            return (node, loma_ir.ConstInt(0))
            # return super().mutate_const_int(node)

        def mutate_var(self, node):
            if node.t == loma_ir.Int() and isinstance(node.t, loma_ir.Int):
                return (node, loma_ir.ConstInt(0))
            elif isinstance(node.t, loma_ir.Array) or isinstance(
                node.t, loma_ir.Struct
            ):
                return node
            return (
                loma_ir.StructAccess(node, "val"),
                loma_ir.StructAccess(node, "dval"),
            )

        def mutate_array_access(self, node):
            arr = self.mutate_expr(node.array)
            idx = self.mutate_expr(node.index)

            if isinstance(idx, tuple):
                idx = idx[0]
            if isinstance(arr, tuple):
                arr = arr[0]

            return_dstruct = autodiff.type_to_diff_type(diff_structs, node.t)

            if arr.t and arr.t.t == loma_ir.Int() and isinstance(arr.t.t, loma_ir.Int):
                val = loma_ir.ArrayAccess(
                    arr, idx, lineno=node.lineno, t=return_dstruct
                )

                d_val = loma_ir.ConstInt(0)
            else:
                val = loma_ir.StructAccess(
                    loma_ir.ArrayAccess(arr, idx, lineno=node.lineno, t=return_dstruct),
                    "val",
                )

                d_val = loma_ir.StructAccess(
                    loma_ir.ArrayAccess(arr, idx, lineno=node.lineno, t=return_dstruct),
                    "dval",
                )

            return (val, d_val)

        def mutate_struct_access(self, node):
            if node.t == loma_ir.Int() and isinstance(node.t, loma_ir.Int):
                return (node, loma_ir.ConstInt(0))
            elif isinstance(node.t, loma_ir.Array):
                return (node, None)

            val = loma_ir.StructAccess(node, "val")
            dval = loma_ir.StructAccess(node, "dval")

            return (val, dval)

        def mutate_add(self, node):
            left_exp = self.mutate_expr(node.left)
            right_exp = self.mutate_expr(node.right)

            val_add = loma_ir.BinaryOp(loma_ir.Add(), left_exp[0], right_exp[0])
            dval_add = loma_ir.BinaryOp(loma_ir.Add(), left_exp[1], right_exp[1])

            return (val_add, dval_add)

        def mutate_sub(self, node):
            left_exp = self.mutate_expr(node.left)
            right_exp = self.mutate_expr(node.right)

            val_add = loma_ir.BinaryOp(loma_ir.Sub(), left_exp[0], right_exp[0])
            dval_add = loma_ir.BinaryOp(loma_ir.Sub(), left_exp[1], right_exp[1])

            return (val_add, dval_add)

        def mutate_mul(self, node):
            left_exp = self.mutate_expr(node.left)
            right_exp = self.mutate_expr(node.right)

            val_mul = loma_ir.BinaryOp(loma_ir.Mul(), left_exp[0], right_exp[0])

            dval_mul_1 = loma_ir.BinaryOp(loma_ir.Mul(), left_exp[0], right_exp[1])
            dval_mul_2 = loma_ir.BinaryOp(loma_ir.Mul(), left_exp[1], right_exp[0])
            dval_mul_final = loma_ir.BinaryOp(loma_ir.Add(), dval_mul_1, dval_mul_2)

            return (val_mul, dval_mul_final)

        def mutate_div(self, node):
            left_exp = self.mutate_expr(node.left)
            right_exp = self.mutate_expr(node.right)

            val_mul = loma_ir.BinaryOp(loma_ir.Div(), left_exp[0], right_exp[0])

            dval_mul_1 = loma_ir.BinaryOp(loma_ir.Mul(), left_exp[1], right_exp[0])
            dval_mul_2 = loma_ir.BinaryOp(loma_ir.Mul(), left_exp[0], right_exp[1])
            dval_numerator = loma_ir.BinaryOp(loma_ir.Sub(), dval_mul_1, dval_mul_2)
            dval_denominator = loma_ir.BinaryOp(
                loma_ir.Mul(), right_exp[0], right_exp[0]
            )
            dval_final = loma_ir.BinaryOp(
                loma_ir.Div(), dval_numerator, dval_denominator
            )

            return (val_mul, dval_final)
        
        def mutate_less(self, node):
            left, _ = self.mutate_expr(node.left)
            right, _ = self.mutate_expr(node.right)

            return [loma_ir.BinaryOp(\
                loma_ir.Less(),
                left,
                right,
                lineno = node.lineno,
                t = node.t), None]
            
        def mutate_greater(self, node):
            left, _ = self.mutate_expr(node.left)
            right, _ = self.mutate_expr(node.right)

            return [loma_ir.BinaryOp(\
                loma_ir.Greater(),
                left,
                right,
                lineno = node.lineno,
                t = node.t), None]

        def mutate_call(self, node):
            call_dstruct = autodiff.type_to_diff_type(diff_structs, node.t)
            mutated_expression = [self.mutate_expr(arg) for arg in node.args]
            mutated_args = list(chain.from_iterable(mutated_expression))
            val = None
            dval = None

            x_val = mutated_args[0]
            x_dval = mutated_args[1]

            match node.id:
                case "sin":

                    val = loma_ir.Call(
                        node.id, [x_val], lineno=node.lineno, t=call_dstruct
                    )
                    dval = loma_ir.BinaryOp(
                        loma_ir.Mul(),
                        loma_ir.Call(
                            "cos", [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                        x_dval,
                    )
                case "cos":
                    val = loma_ir.Call(
                        node.id, [x_val], lineno=node.lineno, t=call_dstruct
                    )
                    dval_mul = loma_ir.BinaryOp(
                        loma_ir.Mul(),
                        loma_ir.Call(
                            "sin", [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                        x_dval,
                    )
                    dval = loma_ir.BinaryOp(
                        loma_ir.Mul(), dval_mul, loma_ir.ConstFloat(-1.0)
                    )
                case "sqrt":
                    val = loma_ir.Call(
                        node.id, [x_val], lineno=node.lineno, t=call_dstruct
                    )
                    dval_mul = loma_ir.BinaryOp(
                        loma_ir.Mul(), loma_ir.ConstFloat(0.5), x_dval
                    )

                    dval = loma_ir.BinaryOp(
                        loma_ir.Div(),
                        dval_mul,
                        loma_ir.Call(
                            node.id, [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                    )
                case "pow":
                    y_val, y_dval = mutated_args[2], mutated_args[3]
                    val = loma_ir.Call(
                        node.id, [x_val, y_val], lineno=node.lineno, t=call_dstruct
                    )

                    dval_mul_1 = loma_ir.BinaryOp(
                        loma_ir.Mul(), x_dval, y_val
                    )  # dx * y
                    y_val_less_1 = loma_ir.BinaryOp(
                        loma_ir.Sub(), y_val, loma_ir.ConstFloat(1.0)
                    )
                    dval_mul_2 = loma_ir.BinaryOp(
                        loma_ir.Mul(),
                        dval_mul_1,
                        loma_ir.Call(
                            node.id,
                            [x_val, y_val_less_1],
                            lineno=node.lineno,
                            t=call_dstruct,
                        ),
                    )  # dx * y * x^y-1

                    dval_mul_3 = loma_ir.BinaryOp(
                        loma_ir.Mul(), y_dval, val
                    )  # dy * x^y
                    dval_mul_4 = loma_ir.BinaryOp(
                        loma_ir.Mul(),
                        dval_mul_3,
                        loma_ir.Call(
                            "log", [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                    )  # dy * x^y * log(x)

                    # dx * y * x^y-1 +  dy * x^y * log(x)
                    dval = loma_ir.BinaryOp(loma_ir.Add(), dval_mul_2, dval_mul_4)
                case "exp":
                    val = loma_ir.Call(
                        node.id, [x_val], lineno=node.lineno, t=call_dstruct
                    )
                    dval = loma_ir.BinaryOp(
                        loma_ir.Mul(),
                        x_dval,
                        loma_ir.Call(
                            node.id, [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                    )
                case "log":
                    val = loma_ir.Call(
                        node.id, [x_val], lineno=node.lineno, t=call_dstruct
                    )
                    dval = loma_ir.BinaryOp(loma_ir.Div(), x_dval, x_val)
                case "int2float":
                    return (
                        loma_ir.Call(
                            node.id, [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                        loma_ir.ConstFloat(0.0),
                    )
                case "float2int":
                    return (
                        loma_ir.Call(
                            node.id, [x_val], lineno=node.lineno, t=call_dstruct
                        ),
                        loma_ir.ConstInt(0),
                    )
                case _ :
                    dfloat_new_args = []
                    fwd_func_id = func_to_fwd[node.id]
                    ## Check if a param is of type Out, add original param in that case
                    for i, arg in enumerate(mutated_expression):
                        called_func_def = funcs[node.id]
                        if called_func_def.args[i].i ==loma_ir.Out():
                            dfloat_new_args.append(node.args[i])
                        else:
                            dfloat_new_args.append(loma_ir.Call('make__dfloat', [arg[0], arg[1]]))
                    if node.t == loma_ir.Float():
                        val = loma_ir.StructAccess(loma_ir.Call(fwd_func_id, dfloat_new_args), 'val')
                        dval = loma_ir.StructAccess(loma_ir.Call(fwd_func_id, dfloat_new_args), 'dval')
                        return val, dval
                    else:
                        return loma_ir.Call(fwd_func_id, dfloat_new_args), None
            return (val, dval)
        
        def mutate_call_stmt(self, node):
            mutated_call = self.mutate_expr(node.call)
            return loma_ir.CallStmt(\
                mutated_call[0],
                lineno = node.lineno)

    return FwdDiffMutator().mutate_function_def(func)

