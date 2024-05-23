import ir

ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irmutator
import autodiff
import string
import random


# From https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
def random_id_generator(
    size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits
):
    return "".join(random.choice(chars) for _ in range(size))


def reverse_diff(
    diff_func_id: str,
    structs: dict[str, loma_ir.Struct],
    funcs: dict[str, loma_ir.func],
    diff_structs: dict[str, loma_ir.Struct],
    func: loma_ir.FunctionDef,
    func_to_rev: dict[str, str],
) -> loma_ir.FunctionDef:
    """Given a primal loma function func, apply reverse differentiation
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
    func_to_rev - mapping from primal function ID to its reverse differentiation
    """

    # Some utility functions you can use for your homework.
    def type_to_string(t):
        match t:
            case loma_ir.Int():
                return "int"
            case loma_ir.Float():
                return "float"
            case loma_ir.Array():
                return "array_" + type_to_string(t.t)
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
                    target_m = loma_ir.StructAccess(target, m.id, t=m.t)
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
                                target_m, loma_ir.ConstInt(i), t=m.t.t
                            )
                            stmts += assign_zero(target_m)
                return stmts
            case _:
                assert False

    def accum_deriv(target, deriv, overwrite):
        match target.t:
            case loma_ir.Int():
                return []
            case loma_ir.Float():
                if overwrite:
                    return [loma_ir.Assign(target, deriv)]
                else:
                    return [
                        loma_ir.Assign(
                            target, loma_ir.BinaryOp(loma_ir.Add(), target, deriv)
                        )
                    ]
            case loma_ir.Struct():
                s = target.t
                stmts = []
                for m in s.members:
                    target_m = loma_ir.StructAccess(target, m.id, t=m.t)
                    deriv_m = loma_ir.StructAccess(deriv, m.id, t=m.t)
                    if isinstance(m.t, loma_ir.Float):
                        stmts += accum_deriv(target_m, deriv_m, overwrite)
                    elif isinstance(m.t, loma_ir.Int):
                        pass
                    elif isinstance(m.t, loma_ir.Struct):
                        stmts += accum_deriv(target_m, deriv_m, overwrite)
                    else:
                        assert isinstance(m.t, loma_ir.Array)
                        assert m.t.static_size is not None
                        for i in range(m.t.static_size):
                            target_m = loma_ir.ArrayAccess(
                                target_m, loma_ir.ConstInt(i), t=m.t.t
                            )
                            deriv_m = loma_ir.ArrayAccess(
                                deriv_m, loma_ir.ConstInt(i), t=m.t.t
                            )
                            stmts += accum_deriv(target_m, deriv_m, overwrite)
                return stmts
            case _:
                assert False

    # A utility class that you can use for HW3.
    # This mutator normalizes each call expression into
    # f(x0, x1, ...)
    # where x0, x1, ... are all loma_ir.Var or
    # loma_ir.ArrayAccess or loma_ir.StructAccess
    # Furthermore, it normalizes all Assign statements
    # with a function call
    # z = f(...)
    # into a declaration followed by an assignment
    # _tmp : [z's type]
    # _tmp = f(...)
    # z = _tmp
    class CallNormalizeMutator(irmutator.IRMutator):
        def mutate_function_def(self, node):
            self.tmp_count = 0
            self.tmp_declare_stmts = []
            new_body = [self.mutate_stmt(stmt) for stmt in node.body]
            new_body = irmutator.flatten(new_body)

            new_body = self.tmp_declare_stmts + new_body

            return loma_ir.FunctionDef(
                node.id,
                node.args,
                new_body,
                node.is_simd,
                node.is_openMpi,
                node.ret_type,
                lineno=node.lineno,
            )

        def mutate_return(self, node):
            self.tmp_assign_stmts = []
            val = self.mutate_expr(node.val)
            return self.tmp_assign_stmts + [loma_ir.Return(val, lineno=node.lineno)]

        def mutate_declare(self, node):
            self.tmp_assign_stmts = []
            val = None
            if node.val is not None:
                val = self.mutate_expr(node.val)
            return self.tmp_assign_stmts + [
                loma_ir.Declare(node.target, node.t, val, lineno=node.lineno)
            ]

        def mutate_assign(self, node):
            self.tmp_assign_stmts = []
            target = self.mutate_expr(node.target)
            self.has_call_expr = False
            val = self.mutate_expr(node.val)
            if self.has_call_expr:
                # turn the assignment into a declaration plus
                # an assignment
                self.tmp_count += 1
                tmp_name = f'_call_t_{self.tmp_count}_{random_id_generator()}'
                self.tmp_count += 1
                self.tmp_declare_stmts.append(loma_ir.Declare(\
                    tmp_name,
                    target.t,
                    lineno = node.lineno))
                tmp_var = loma_ir.Var(tmp_name, t = target.t)
                assign_tmp = loma_ir.Assign(\
                    tmp_var,
                    val,
                    lineno = node.lineno)
                assign_target = loma_ir.Assign(\
                    target,
                    tmp_var,
                    lineno = node.lineno)
                return self.tmp_assign_stmts + [assign_tmp, assign_target]
            else:
                return self.tmp_assign_stmts + [loma_ir.Assign(\
                    target,
                    val,
                    lineno = node.lineno)]

        def mutate_call_stmt(self, node):
            self.tmp_assign_stmts = []
            call = self.mutate_expr(node.call)
            return self.tmp_assign_stmts + [loma_ir.CallStmt(call, lineno=node.lineno)]

        def mutate_call(self, node):
            self.has_call_expr = True
            new_args = []
            for arg in node.args:
                if (
                    not isinstance(arg, loma_ir.Var)
                    and not isinstance(arg, loma_ir.ArrayAccess)
                    and not isinstance(arg, loma_ir.StructAccess)
                ):
                    arg = self.mutate_expr(arg)
                    tmp_name = f"_call_t_{self.tmp_count}_{random_id_generator()}"
                    self.tmp_count += 1
                    tmp_var = loma_ir.Var(tmp_name, t=arg.t)
                    self.tmp_declare_stmts.append(loma_ir.Declare(tmp_name, arg.t))
                    self.tmp_assign_stmts.append(loma_ir.Assign(tmp_var, arg))
                    new_args.append(tmp_var)
                else:
                    new_args.append(arg)
            return loma_ir.Call(node.id, new_args, t=node.t)

    # HW2 happens here. Modify the following IR mutators to perform
    # reverse differentiation.

    def check_lhs_is_output_arg(lhs, output_args):
        match lhs:
            case loma_ir.Var():
                return lhs.id in output_args
            case loma_ir.StructAccess():
                return check_lhs_is_output_arg(lhs.struct, output_args)
            case loma_ir.ArrayAccess():
                return check_lhs_is_output_arg(lhs.array, output_args)
            case _:
                return False

    class FwdPassMutator(irmutator.IRMutator):

        def __init__(self, output_args):
            self.var_count = 0
            self.output_args = output_args
            self.f_loop_counter_count = 0

        # Since while can also have a body need to approximate tape length based on that as well
        def unwrap_while_and_get_approx_tape_len(self, body, declare_loop_ctr_count):
            loop_ctr_declare = []
            
            tape_len = len(body)
            body = irmutator.flatten(body)
            for stmt in body:
                if isinstance(stmt, loma_ir.While):
                    tape_len+=stmt.max_iter
                    loop_ctr_declare.append(loma_ir.Declare(
                    target=f'_loop_ctr_{declare_loop_ctr_count}', t=loma_ir.Int(), val=loma_ir.ConstInt(0)))
                    declare_loop_ctr_count+=1
                    added_len, added_declare=self.unwrap_while_and_get_approx_tape_len(stmt.body, declare_loop_ctr_count)
                    loop_ctr_declare+=added_declare
                    tape_len+=added_len
                    
            return tape_len, loop_ctr_declare


        def mutate_function_def(self, node):

            # Need to iterate the function once to find approximate length of tape 
            # Better way?
            declare_loop_ctr_count = 0
            approx_tape_length, loop_ctr_declare = self.unwrap_while_and_get_approx_tape_len(node.body, declare_loop_ctr_count)

            tape_declare = loma_ir.Declare(
                target="tape",
                t=loma_ir.Array(t=loma_ir.Float(), static_size=approx_tape_length),
            )
            ptr_declare = loma_ir.Declare(
                target="tape_ptr", t=loma_ir.Int(), val=loma_ir.ConstInt(0)
            )
           
            
            self.declare_stmts = []
            new_body = [tape_declare, ptr_declare]
            
            for stmt in node.body:

                if isinstance(stmt, loma_ir.Assign) and isinstance(
                    stmt.target.t, loma_ir.Struct
                ):
                    continue
                if not isinstance(stmt, loma_ir.Return):
                    mutated_stmt = self.mutate_stmt(stmt)

                    if (
                        isinstance(stmt, loma_ir.Assign)
                        or isinstance(stmt, loma_ir.Declare)
                    ) and not check_lhs_is_output_arg(stmt.target, self.output_args):
                        new_body.append(mutated_stmt)
                    else: 
                        new_body.append(mutated_stmt)

            new_body = irmutator.flatten([loop_ctr_declare, new_body])
            new_func = loma_ir.FunctionDef(
                diff_func_id, node.args, new_body, node.is_simd, node.is_openMpi, None
            )

            return new_func

        def mutate_declare(self, node):
            stmt = loma_ir.Declare(f"_d{node.target}", node.t)
            self.declare_stmts.append(stmt)
            return super().mutate_declare(node)

        def mutate_assign(self, node):
            output_args = [arg.id for arg in func.args if arg.i == loma_ir.Out()]
            
            if (isinstance(node.target, loma_ir.Var) and not node.target.id in output_args):
                add_to_tape = loma_ir.Assign(
                        target=loma_ir.ArrayAccess(
                            loma_ir.Var("tape"), loma_ir.Var("tape_ptr")
                        ),
                        val=node.target,
                    )
                incr_ptr = loma_ir.Assign(
                    loma_ir.Var("tape_ptr"),
                    loma_ir.BinaryOp(
                        loma_ir.Add(), loma_ir.Var("tape_ptr"), loma_ir.ConstInt(1)
                    ),
                )
                assign = super().mutate_assign(node)
                return [add_to_tape, assign, incr_ptr]
            else:
                super().mutate_assign(node)
            return []

        def mutate_var(self, node):
            self.var_count += 1
            return super().mutate_var(node)
        
        def mutate_call_stmt(self, node):
            return [] 

        # Increment loop counter at the start
        def mutate_while(self, node):
            stmts = []
            
            new_cond= self.mutate_expr(node.cond)
            new_body = [self.mutate_stmt(stmt) for stmt in node.body]
            # Important: mutate_stmt can return a list of statements. We need to flatten the list.
            new_body = irmutator.flatten(new_body)

            loop_ctr = loma_ir.Var(f'_loop_ctr_{self.f_loop_counter_count}')
            new_body.append(loma_ir.Assign(loop_ctr, loma_ir.BinaryOp(loma_ir.Add(), loop_ctr, loma_ir.ConstInt(1))))

            while_stmt = loma_ir.While(\
                new_cond,
                node.max_iter,
                new_body,
                lineno = node.lineno)
            stmts.append(while_stmt) 
            self.f_loop_counter_count+=1
            return stmts

    # Apply the differentiation.
    class RevDiffMutator(irmutator.IRMutator):
        def mutate_function_def(self, node):

            # Check if node is simd
            self.is_simd = node.is_simd

            # Normalize node
            node = CallNormalizeMutator().mutate_function_def(node)

            new_args = []
            self.output_args = []
            for arg in node.args:
                if arg.i == loma_ir.In():
                    new_args.append(arg)
                    new_arg_id = "_d" + arg.id
                    new_args.append(
                        loma_ir.Arg(id=new_arg_id, t=arg.t, i=loma_ir.Out())
                    )
                elif arg.i == loma_ir.Out():
                    new_arg_id = "_d" + arg.id
                    new_args.append(loma_ir.Arg(new_arg_id, t=arg.t, i=loma_ir.In()))
                    self.output_args.append(arg.id)

            if node.ret_type != None:
                new_args.append(
                    loma_ir.Arg(id="_dreturn", t=node.ret_type, i=loma_ir.In())
                )

            # forward pass
            fm = FwdPassMutator(self.output_args)
            new_fwd_func = fm.mutate_function_def(node)
            new_body_fwd = [stmt for stmt in new_fwd_func.body]
            new_body_fwd = irmutator.flatten(new_body_fwd)
            new_body_fwd += fm.declare_stmts

            # a list of temporary adjoint variables
            temp_adjoints = []
            # a variable to keep track of which adjoint to use
            self.tmp_adjoint_cnt = 0
            # assign statement to be processes later after adjoints are computed
            self.assign_dalyed_adjoints = []
            # Should a delay assign way be used
            self.delay_ajoints = False
            # Skip target zero
            self.skip_target_zero = False
            # Loop counter count
            self.r_loop_counter_count = 0

            for i in range(fm.var_count+5):
                temp_adjoints.append(
                    loma_ir.Declare("_adj_" + str(i), t=loma_ir.Float())
                )

            # reverse pass
            new_body_rev = [self.mutate_stmt(stmt) for stmt in reversed(node.body)]
            new_body_rev = irmutator.flatten(new_body_rev)

            new_body = new_body_fwd + temp_adjoints + new_body_rev

            new_func = loma_ir.FunctionDef(
                diff_func_id, new_args, new_body, node.is_simd, node.is_openMpi, None
            )

            return new_func

        def mutate_return(self, node):

            self.adjoint = loma_ir.Var("_dreturn")
            stmts = self.mutate_expr(node.val)
            self.adjoint = None
            return stmts

        def mutate_declare(self, node):

            if node.val != None:
                self.adjoint = loma_ir.Var(f"_d{node.target}")
                stmts = self.mutate_expr(node.val)
                self.adjoint = None
                return stmts
            return []

        def mutate_assign(self, node):
            # stack ptr -1 and stack.pop()
            dec_ptr = []
            pop_from_tape = []
            if not check_lhs_is_output_arg(node.target, self.output_args):
                if isinstance(node.target.t, loma_ir.Struct):
                    pass
                else:
                    dec_ptr = loma_ir.Assign(
                        loma_ir.Var("tape_ptr"),
                        loma_ir.BinaryOp(
                            loma_ir.Sub(), loma_ir.Var("tape_ptr"), loma_ir.ConstInt(1)
                        ),
                    )
                    pop_from_tape = loma_ir.Assign(
                        target=node.target,
                        val=loma_ir.ArrayAccess(
                            loma_ir.Var("tape"), loma_ir.Var("tape_ptr")
                        ),
                    )

            if isinstance(node.target, loma_ir.ArrayAccess):
                self.adjoint = loma_ir.ArrayAccess(
                    loma_ir.Var("_d" + node.target.array.id), node.target.index
                )
            elif isinstance(node.target, loma_ir.StructAccess):
                self.adjoint = loma_ir.StructAccess(
                    struct=loma_ir.Var(
                        id="_d" + node.target.struct.id,
                        t=loma_ir.Struct(
                            id=node.target.struct.t.id,
                            members=node.target.struct.t.members,
                        ),
                    ),
                    member_id=node.target.member_id,
                )
            else:
                self.adjoint = loma_ir.Var(f"_d{node.target.id}")

            if not isinstance(node.target.t, loma_ir.Struct):
                self.delay_ajoints = True
            rhs = self.mutate_expr(node.val)
            self.delay_ajoints = False

            # Reset target to zero
            target_zero = []
            if check_lhs_is_output_arg(node.target, self.output_args):
                pass
            elif isinstance(node.target, loma_ir.ArrayAccess):
                target_zero = loma_ir.Assign(
                    target=loma_ir.ArrayAccess(
                        loma_ir.Var("_d" + node.target.array.id), node.target.index
                    ),
                    val=loma_ir.ConstFloat(0.0),
                )
            elif isinstance(node.target, loma_ir.StructAccess):
                target_zero = loma_ir.Assign(
                    target=loma_ir.StructAccess(
                        struct=loma_ir.Var(
                            id="_d" + node.target.struct.id,
                            t=loma_ir.Struct(
                                id=node.target.struct.t.id,
                                members=node.target.struct.t.members,
                            ),
                        ),
                        member_id=node.target.member_id,
                    ),
                    val=loma_ir.ConstFloat(0.0),
                )
            elif isinstance(node.target.t, loma_ir.Struct):
                pass
            elif isinstance(node.val, loma_ir.Call) and self.skip_target_zero:
                self.skip_target_zero = False
                pass
            else:
                target_zero = loma_ir.Assign(
                    target=loma_ir.Var(f"_d{node.target.id}"),
                    val=loma_ir.ConstFloat(0.0),
                )

            ## Stack pop + assign + all adjoints
            result = [
                dec_ptr,
                pop_from_tape,
                rhs,
                target_zero,
                self.assign_dalyed_adjoints,
            ]
            self.adjoint = None
            self.assign_dalyed_adjoints = []
            return result

        def mutate_ifelse(self, node):
            new_cond = node.cond
            new_then_stmts = [self.mutate_stmt(stmt) for stmt in reversed(node.then_stmts)]
            new_else_stmts = [self.mutate_stmt(stmt) for stmt in reversed(node.else_stmts)]
            # Important: mutate_stmt can return a list of statements. We need to flatten the lists.
            new_then_stmts = irmutator.flatten(new_then_stmts)
            new_else_stmts = irmutator.flatten(new_else_stmts)
            return loma_ir.IfElse(
                new_cond, new_then_stmts, new_else_stmts, lineno=node.lineno
            )

        # Should be handles by mutate_call
        def mutate_call_stmt(self, node):
            mutated_call = self.mutate_expr(node.call)
            print(mutated_call)
            return mutated_call

        # Decrement counter in the body
        def mutate_while(self, node):
            local_loop_counter = loma_ir.Var(f'_loop_ctr_{self.r_loop_counter_count}')
            new_cond = loma_ir.BinaryOp(loma_ir.Greater(), local_loop_counter,  loma_ir.ConstInt(0))
            new_body = [self.mutate_stmt(stmt) for stmt in reversed(node.body)]
            # Important: mutate_stmt can return a list of statements. We need to flatten the list.
            new_body = irmutator.flatten(new_body)
            new_body.append(loma_ir.Assign(local_loop_counter, loma_ir.BinaryOp(loma_ir.Sub(), local_loop_counter, loma_ir.ConstInt(1))))
            self.r_loop_counter_count+=1
            return loma_ir.While(\
                new_cond,
                node.max_iter,
                new_body,
                lineno = node.lineno)

        def mutate_const_float(self, node):
            return []

        def mutate_const_int(self, node):
            return []

        def mutate_var(self, node):

            # In case of an assign store the adjoint and use it later
            dx = loma_ir.Var("_d" + node.id)
            if self.delay_ajoints:
                temp_adj = loma_ir.Var("_adj_" + str(self.tmp_adjoint_cnt))
                stmts = [loma_ir.Assign(temp_adj, self.adjoint)]
                if self.is_simd:
                    self.assign_dalyed_adjoints.append(
                        loma_ir.CallStmt(loma_ir.Call('atomic_add', [dx, self.adjoint]))
                    )
                else:
                    self.assign_dalyed_adjoints.append(
                        loma_ir.Assign(dx, loma_ir.BinaryOp(loma_ir.Add(), dx, temp_adj))
                    )
                self.tmp_adjoint_cnt += 1
            else:
                if isinstance(node.t, loma_ir.Struct):
                    stmts = [loma_ir.Assign(loma_ir.Var("_d" + node.id), self.adjoint)]
                else:
                    stmts = [
                        loma_ir.Assign(
                            dx, loma_ir.BinaryOp(loma_ir.Add(), dx, self.adjoint)
                        )
                    ]
            return stmts

        def mutate_array_access(self, node):

            if not isinstance(node.array, loma_ir.Var):
                mutated_node = loma_ir.ArrayAccess(
                    self.mutate_expr(node.array)[0].target, node.index, t=node.t
                )
            else:
                mutated_node = loma_ir.ArrayAccess(
                    array=loma_ir.Var("_d" + node.array.id), index=node.index
                )
            stmts = [
                loma_ir.Assign(
                        mutated_node,
                        loma_ir.BinaryOp(loma_ir.Add(), mutated_node, self.adjoint),
                )
            ]

            return stmts

        def mutate_struct_access(self, node):

            mutated_node = loma_ir.StructAccess(
                struct=loma_ir.Var(
                    id="_d" + node.struct.id,
                    t=loma_ir.Struct(
                        id=node.struct.t.id, members=node.struct.t.members
                    ),
                ),
                member_id=node.member_id,
            )

            if self.delay_ajoints:
                temp_adj = loma_ir.Var("_adj_" + str(self.tmp_adjoint_cnt))
                stmts = [loma_ir.Assign(temp_adj, self.adjoint)]
                self.assign_dalyed_adjoints.append(
                    loma_ir.Assign(
                        mutated_node,
                        loma_ir.BinaryOp(loma_ir.Add(), mutated_node, temp_adj),
                    )
                )
                self.tmp_adjoint_cnt += 1
            else:
                stmts = [
                    loma_ir.Assign(
                        mutated_node,
                        loma_ir.BinaryOp(loma_ir.Add(), mutated_node, self.adjoint),
                    )
                ]

            return stmts

        def mutate_add(self, node):

            stmts_left = self.mutate_expr(node.left)
            stmts_right = self.mutate_expr(node.right)
            return stmts_left + stmts_right

        def mutate_sub(self, node):

            stmts_left = self.mutate_expr(node.left)
            old_adjoint = self.adjoint
            self.adjoint = loma_ir.BinaryOp(
                loma_ir.Sub(), loma_ir.ConstFloat(0.0), self.adjoint
            )
            stmts_right = self.mutate_expr(node.right)
            self.adjoint = old_adjoint
            return stmts_left + stmts_right

        def mutate_mul(self, node):

            old_adjoint = self.adjoint
            self.adjoint = loma_ir.BinaryOp(loma_ir.Mul(), self.adjoint, node.right)
            stmts_left = self.mutate_expr(node.left)
            self.adjoint = old_adjoint

            old_adjoint = self.adjoint
            self.adjoint = loma_ir.BinaryOp(loma_ir.Mul(), self.adjoint, node.left)
            stmts_right = self.mutate_expr(node.right)
            self.adjoint = old_adjoint

            return stmts_left + stmts_right

        def mutate_div(self, node):

            old_adjoint = self.adjoint
            self.adjoint = loma_ir.BinaryOp(loma_ir.Div(), self.adjoint, node.right)
            stmts_left = self.mutate_expr(node.left)
            self.adjoint = old_adjoint

            old_adjoint = self.adjoint
            self.adjoint = loma_ir.BinaryOp(
                loma_ir.Sub(), loma_ir.ConstFloat(0.0), self.adjoint
            )
            numerator = loma_ir.BinaryOp(loma_ir.Mul(), self.adjoint, node.left)
            denominator = loma_ir.BinaryOp(loma_ir.Mul(), node.right, node.right)
            self.adjoint = loma_ir.BinaryOp(loma_ir.Div(), numerator, denominator)
            stmts_right = self.mutate_expr(node.right)
            self.adjoint = old_adjoint

            return stmts_left + stmts_right

        def mutate_call(self, node):
            mutated_statements = []
            match node.id:
                case "sin":
                    old_adjoint = self.adjoint
                    self.adjoint = loma_ir.BinaryOp(
                        loma_ir.Mul(), self.adjoint, loma_ir.Call("cos", node.args)
                    )
                    for arg in node.args:
                        mutated_statements.append(self.mutate_expr(arg))

                    self.adjoint = old_adjoint
                case "cos":
                    old_adjoint = self.adjoint
                    self.adjoint = loma_ir.BinaryOp(
                        loma_ir.Mul(),
                        self.adjoint,
                        loma_ir.BinaryOp(
                            loma_ir.Mul(),
                            loma_ir.ConstInt(-1),
                            loma_ir.Call("sin", node.args),
                        ),
                    )
                    for arg in node.args:
                        mutated_statements.append(self.mutate_expr(arg))

                    self.adjoint = old_adjoint
                case "sqrt":
                    old_adjoint = self.adjoint
                    self.adjoint = loma_ir.BinaryOp(
                        loma_ir.Div(),
                        self.adjoint,
                        loma_ir.BinaryOp(
                            loma_ir.Mul(),
                            loma_ir.ConstInt(2),
                            loma_ir.Call("sqrt", node.args),
                        ),
                    )
                    for arg in node.args:
                        mutated_statements.append(self.mutate_expr(arg))

                    self.adjoint = old_adjoint
                case "pow":
                    base = node.args[0]
                    power = node.args[1]
                    old_adjoint = self.adjoint

                    temp = loma_ir.Call(
                        "pow",
                        [
                            base,
                            loma_ir.BinaryOp(
                                loma_ir.Sub(), power, loma_ir.ConstFloat(1.0)
                            ),
                        ],
                    )
                    diff_base = loma_ir.BinaryOp(loma_ir.Mul(), power, temp)
                    self.adjoint = loma_ir.BinaryOp(
                        loma_ir.Mul(), self.adjoint, diff_base
                    )
                    mutated_statements.append(self.mutate_expr(base))
                    self.adjoint = old_adjoint

                    diff_power = loma_ir.BinaryOp(
                        loma_ir.Mul(), loma_ir.Call("log", [base]), node
                    )
                    self.adjoint = loma_ir.BinaryOp(
                        loma_ir.Mul(), self.adjoint, diff_power
                    )
                    mutated_statements.append(self.mutate_expr(power))
                    self.adjoint = old_adjoint
                case "exp":
                    old_adjoint = self.adjoint
                    self.adjoint = loma_ir.BinaryOp(loma_ir.Mul(), self.adjoint, node)
                    for arg in node.args:
                        mutated_statements.append(self.mutate_expr(arg))

                    self.adjoint = old_adjoint
                case "log":
                    old_adjoint = self.adjoint
                    self.adjoint = loma_ir.BinaryOp(
                        loma_ir.Div(), self.adjoint, node.args[0]
                    )
                    for arg in node.args:
                        mutated_statements.append(self.mutate_expr(arg))

                    self.adjoint = old_adjoint
                case 'int2float':
                    # don't propagate the derivatives
                    return []
                case 'float2int':
                    # don't propagate the derivatives
                    return []
                case 'thread_id':
                    # don't propagate the derivatives
                    return []
                case 'atomic_add':
                    # Perform rev diff of atomic add
                    self.adjoint = loma_ir.Var("_d" + node.args[0].id)
                    left = self.mutate_expr(node.args[1])
                    left = left[0].target
                    right = self.mutate_expr(node.args[0])
                    right = right[0].target  
                    mutated_statements.append(loma_ir.CallStmt(loma_ir.Call('atomic_add', 
                                                               [left, right])))
                case _:
                        # Delay adjoints in case of assign
                        if self.delay_ajoints:
                            temp_adj = loma_ir.Var("_adj_" + str(self.tmp_adjoint_cnt))
                            mutated_statements.append(loma_ir.Assign(temp_adj, self.adjoint))
                            mutated_statements.append(loma_ir.Assign(loma_ir.Var(self.adjoint.id),loma_ir.ConstFloat(0.0)))
                            self.adjoint = loma_ir.Var('_adj_' + str(self.tmp_adjoint_cnt))
                            self.skip_target_zero = True
                            self.tmp_adjoint_cnt += 1

                        new_args = []
                        called_func_def = funcs[node.id]
                        for i, arg in enumerate(node.args):
                            if not called_func_def.args[i].i ==loma_ir.Out():
                                new_args.append(arg)
                            new_args.append(loma_ir.Var('_d'+ arg.id))
                        rev_func_id = func_to_rev[node.id]
                        original_function = funcs[node.id]

                        if original_function.ret_type != None:
                            new_args.append(self.adjoint)

                        mutated_statements.append(loma_ir.CallStmt(loma_ir.Call(rev_func_id, new_args)))

                        # Assign output variables to zero after function call
                        for i, arg in enumerate(node.args):
                            if called_func_def.args[i].i ==loma_ir.Out() and arg.t == loma_ir.Float():
                                 mutated_statements += [loma_ir.Assign(loma_ir.Var(f"_d{arg.id}"), loma_ir.ConstFloat(0.0))]

            return mutated_statements

    return RevDiffMutator().mutate_function_def(func)
