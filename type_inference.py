import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import autodiff
import attrs
import error
import irmutator
import pretty_print

def fill_in_struct_info(t : loma_ir.type,
                        structs : dict[str, loma_ir.Struct]) -> loma_ir.type:
    """ During parsing, we sometimes leave the struct member information empty.
        Given a loma type where some of the struct member information is missing,
        this function looks up from the provided struct dictionary and fill
        in the missing information.
    """

    match t:
        case loma_ir.Int():
            return t
        case loma_ir.Float():
            return t
        case loma_ir.Array():
            return loma_ir.Array(fill_in_struct_info(t.t, structs), t.static_size)
        case loma_ir.Struct():
            if len(t.members) == 0:
                return structs[t.id]
            else:
                return t
        case _:
            assert False

class TypeInferencer(irmutator.IRMutator):
    """ The TypeInferencer does three things:
        1) It infers the types of all expressions.
        2) It fills in the missing information of struct members during type inference.
        3) It checks if the types match between expressions.
           If not, it raises errors.
    """

    def __init__(self, structs, diff_structs, funcs):
        self.var_types = {}
        self.structs = structs
        self.diff_structs = diff_structs
        self.funcs = funcs

    def lookup_ref_type(self, ref):
        ret_type = None
        match ref:
            case loma_ir.Var():
                ret_type = self.var_types[ref.id]
            case loma_ir.ArrayAccess():
                parent_type = self.lookup_ref_type(ref.array)
                ret_type = parent_type.t
            case loma_ir.StructAccess():
                parent_type = self.lookup_ref_type(ref.struct)
                if not isinstance(parent_type, loma_ir.Struct):
                    # TODO: error message
                    assert False
                for m in parent_type.members:
                    if m.id == ref.member_id:
                        ret_type = m.t
                        break
                if ret_type is None:
                    assert False, f'member {ref.member_id} not found in Struct {parent_type.id}'
            case _:
                # TODO: error message (invalid lhs)
                assert False
        if isinstance(ret_type, loma_ir.Struct) and len(ret_type.members) == 0:
            ret_type = self.structs[ret_type.id]
        return ret_type

    def mutate_function_def(self, node):
        # Go over the arguments and record their types
        self.current_func_args = list(node.args)
        for i, arg in enumerate(node.args):
            t = fill_in_struct_info(arg.t, self.structs)
            self.var_types[arg.id] = t
            self.current_func_args[i] = loma_ir.Arg(arg.id, t, arg.i)
        new_args = self.current_func_args
        
        new_ret_type = node.ret_type
        if isinstance(new_ret_type, loma_ir.Struct) and len(new_ret_type.members) == 0:
            new_ret_type = self.structs[new_ret_type.id]
        self.current_func_ret = new_ret_type

        new_body = [self.mutate_stmt(stmt) for stmt in node.body]
        # Important: mutate_stmt can return a list of statements. We need to flatten the list.
        new_body = irmutator.flatten(new_body)
        return loma_ir.FunctionDef(\
            node.id,
            new_args,
            new_body,
            node.is_simd,
            new_ret_type,
            lineno = node.lineno)

    def mutate_return(self, ret):
        new_val = self.mutate_expr(ret.val)
        if new_val.t == loma_ir.Int() and self.current_func_ret == loma_ir.Float():
            new_val = loma_ir.Call('int2float',
                [new_val], lineno = new_val.lineno, t = loma_ir.Float())
        elif new_val.t == loma_ir.Float() and self.current_func_ret == loma_ir.Int():
            new_val = loma_ir.Call('float2int',
                [new_val], lineno = new_val.lineno, t = loma_ir.Int())
        if new_val.t != self.current_func_ret:
            raise error.ReturnTypeMismatch(ret)
        return loma_ir.Return(\
            new_val,
            lineno = ret.lineno)

    def mutate_declare(self, dec):
        t = dec.t
        if isinstance(t, loma_ir.Struct) and len(t.members) == 0:
            t = self.structs[t.id]
        self.var_types[dec.target] = t
        if dec.val is not None:
            new_val = self.mutate_expr(dec.val)
            if new_val is not None:
                if new_val.t == loma_ir.Int() and t == loma_ir.Float():
                    new_val = loma_ir.Call('int2float',
                        [new_val], lineno = new_val.lineno, t = loma_ir.Float())
                elif new_val.t == loma_ir.Float() and t == loma_ir.Int():
                    new_val = loma_ir.Call('float2int',
                        [new_val], lineno = new_val.lineno, t = loma_ir.Int())
                if new_val.t != t:
                    raise error.DeclareTypeMismatch(dec)
        else:
            new_val = None
        return loma_ir.Declare(\
            dec.target,
            t,
            new_val,
            lineno = dec.lineno)

    def mutate_assign(self, ass):
        new_val = self.mutate_expr(ass.val)
        ref = ass.target
        ref_type = self.lookup_ref_type(ref)
        val_type = new_val.t

        if val_type == loma_ir.Int() and ref_type == loma_ir.Float():
            new_val = loma_ir.Call('int2float',
                [new_val], lineno = new_val.lineno, t = loma_ir.Float())
        elif val_type == loma_ir.Float() and ref_type == loma_ir.Int():
            new_val = loma_ir.Call('float2int',
                [new_val], lineno = new_val.lineno, t = loma_ir.Int())
        if new_val.t != ref_type:
            raise error.AssignTypeMismatch(ass)
        return loma_ir.Assign(\
            self.mutate_expr(ass.target),
            new_val,
            lineno = ass.lineno)

    def mutate_ifelse(self, ifelse):
        new_ifelse = super().mutate_ifelse(ifelse)
        if new_ifelse.cond.t != loma_ir.Int() and \
                new_ifelse.cond.t != loma_ir.Float():
            raise error.IfElseCondTypeMismatch(new_ifelse.cond)
        return new_ifelse

    def mutate_var(self, var):
        new_var = loma_ir.Var(\
            var.id,
            lineno = var.lineno,
            t = self.var_types[var.id])
        return new_var

    def mutate_array_access(self, acc):
        arr = self.mutate_expr(acc.array)
        if not isinstance(arr.t, loma_ir.Array):
            raise error.ArrayAccessTypeMismatch(acc)
        return loma_ir.ArrayAccess(\
            arr,
            self.mutate_expr(acc.index),
            lineno = acc.lineno,
            t = arr.t.t)

    def mutate_struct_access(self, s):
        struct = self.mutate_expr(s.struct)
        if not isinstance(struct.t, loma_ir.Struct):
            raise error.StructAccessTypeMismatch(s)
        if len(struct.t.members) == 0:
            # fill in struct information
            struct = attrs.evolve(struct, t=self.structs[struct.t.id])

        member_type = None
        for m in struct.t.members:
            if m.id == s.member_id:
                member_type = m.t
                break
        if member_type is None:
            raise error.StructMemberNotFound(s)
        if isinstance(member_type, loma_ir.Struct):
            if len(member_type.members) == 0:
                # fill in struct information
                member_type = self.structs[member_type.id]

        return loma_ir.StructAccess(\
            struct,
            s.member_id,
            lineno = s.lineno,
            t = member_type)

    def mutate_const_float(self, con):
        return loma_ir.ConstFloat(\
            con.val,
            lineno = con.lineno,
            t = loma_ir.Float())

    def mutate_const_int(self, con):
        return loma_ir.ConstInt(\
            con.val,
            lineno = con.lineno,
            t = loma_ir.Int())

    def mutate_binary_op(self, expr):
        left = self.mutate_expr(expr.left)
        right = self.mutate_expr(expr.right)
        # Casting rule:
        # int, int -> int
        # int, float / float, int -> float
        # float, float -> float
        if left.t == loma_ir.Int() and right.t == loma_ir.Int():
            inferred_type = loma_ir.Int()
        elif left.t == loma_ir.Int() and right.t == loma_ir.Float():
            inferred_type = loma_ir.Float()
            left = loma_ir.Call('int2float',
                [left], lineno = left.lineno, t = loma_ir.Float())
        elif left.t == loma_ir.Float() and right.t == loma_ir.Int():
            inferred_type = loma_ir.Float()
            right = loma_ir.Call('int2float',
                [right], lineno = right.lineno, t = loma_ir.Float())
        elif left.t == loma_ir.Float() and right.t == loma_ir.Float():
            inferred_type = loma_ir.Float()
        else:
            raise error.BinaryOpTypeMismatch(expr)

        return loma_ir.BinaryOp(\
            expr.op,
            left,
            right,
            lineno = expr.lineno,
            t = inferred_type)

    def mutate_call(self, call):
        args = [self.mutate_expr(arg) for arg in call.args]
        inf_type = None

        # Check for intrinsic functions
        if call.id == 'sin' or \
                call.id == 'cos' or \
                call.id == 'sqrt' or \
                call.id == 'exp' or \
                call.id == 'log':
            if len(args) != 1:
                raise error.CallTypeMismatch(call)
            if args[0].t == loma_ir.Int():
                args[0] = loma_ir.Call('int2float',
                    [args[0]], lineno = args[0].lineno, t = loma_ir.Float())
            if args[0].t != loma_ir.Float():
                raise error.CallTypeMismatch(call)
            inf_type = loma_ir.Float()
        elif call.id == 'int2float':
            if len(args) != 1 or args[0].t != loma_ir.Int():
                raise error.CallTypeMismatch(call)
            inf_type = loma_ir.Float()
        elif call.id == 'float2int':
            if len(args) != 1 or args[0].t != loma_ir.Float():
                raise error.CallTypeMismatch(call)
            inf_type = loma_ir.Int()
        elif call.id == 'pow':
            if len(args) != 2:
                raise error.CallTypeMismatch(call)
            for i in range(2):
                if args[i].t == loma_ir.Int():
                    args[i] = loma_ir.Call('int2float',
                        [args[i]], lineno = args[i].lineno, t = loma_ir.Float())
                if args[i].t != loma_ir.Float():
                    raise error.CallTypeMismatch(call)
            inf_type = loma_ir.Float()
        elif call.id == 'thread_id':
            if len(args) != 0:
                raise error.CallTypeMismatch(call)
            inf_type = loma_ir.Int()
        elif call.id == 'atomic_add':
            if len(args) != 2:
                raise error.CallTypeMismatch(call)
            inf_type = None
        else:
            if call.id not in self.funcs:
                raise error.CallIDNotFound(call)
            f = self.funcs[call.id]
            if isinstance(f, loma_ir.FunctionDef):
                f_args = f.args
                ret_type = f.ret_type
            elif isinstance(f, loma_ir.ForwardDiff):
                primal_f = self.funcs[f.primal_func]
                f_args = [\
                    loma_ir.Arg(arg.id, autodiff.type_to_diff_type(self.diff_structs, arg.t), arg.i) \
                    for arg in primal_f.args]
                ret_type = autodiff.type_to_diff_type(self.diff_structs, primal_f.ret_type)
            elif isinstance(f, loma_ir.ReverseDiff):
                primal_f = self.funcs[f.primal_func]
                f_args = []
                for arg in primal_f.args:
                    if arg.i == loma_ir.In():
                        f_args.append(arg)
                        dvar_id = '_d' + arg.id
                        f_args.append(loma_ir.Arg('_d' + arg.id, arg.t, i = loma_ir.Out()))
                    else:
                        assert arg.i == loma_ir.Out()
                        f_args.append(loma_ir.Arg(arg.id, arg.t, i = loma_ir.In()))
                if primal_f.ret_type is not None:
                    self.return_var_id = '_dreturn'
                    f_args.append(loma_ir.Arg('_dreturn', primal_f.ret_type, i = loma_ir.In()))
                ret_type = None
            if len(args) != len(f_args):
                raise error.CallTypeMismatch(call)
            for i, (call_arg, f_arg) in enumerate(zip(args, f_args)):
                if call_arg.t == loma_ir.Int() and f_arg.t == loma_ir.Float():
                    args[i] = loma_ir.Call('int2float',
                        [args[i]], lineno = args[i].lineno, t = loma_ir.Float())
                    call_arg = args[i]
                elif call_arg.t == loma_ir.Float() and f_arg.t == loma_ir.Int():
                    args[i] = loma_ir.Call('float2int',
                        [args[i]], lineno = args[i].lineno, t = loma_ir.Int())
                    call_arg = args[i]

                if call_arg.t != f_arg.t:
                    raise error.CallTypeMismatch(call)
            inf_type = ret_type

        return loma_ir.Call(\
            call.id,
            args,
            lineno = call.lineno,
            t = inf_type)

def check_and_infer_types(structs : dict[str, loma_ir.Struct],
                          diff_structs : dict[str, loma_ir.Struct],
                          funcs : dict[str, loma_ir.func]):
    for id, f in funcs.items():
        ti = TypeInferencer(structs, diff_structs, funcs)
        funcs[id] = ti.mutate_function(f)
