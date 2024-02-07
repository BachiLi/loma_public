import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def type_to_diff_type(type,
                      diff_structs):
    match type:
        case loma_ir.Int():
            return diff_structs['int']
        case loma_ir.Float():
            return diff_structs['float']
        case loma_ir.Array():
            return loma_ir.Array(\
                type_to_diff_type(type.t, diff_structs),
                type.static_size)
        case loma_ir.Struct():
            return diff_structs[type.id]
        case None:
            return None
        case _:
            assert False, f'Unhandled type {type}'

def replace_diff_types(diff_structs,
                       func):
    # Go through the code and replace each type of Diff[] with the actual type
    # Note that we do not allow repeat applications of Diff[]
    def _replace_diff_type(t):
        match t:
            case loma_ir.Int():
                return loma_ir.Int()
            case loma_ir.Float():
                return loma_ir.Float()
            case loma_ir.Array():
                return loma_ir.Array(\
                    _replace_diff_type(t.t),
                    t.static_size)
            case loma_ir.Struct():
                return t
            case loma_ir.Diff():
                t = _replace_diff_type(t.t)
                if t == loma_ir.Int():
                    return diff_structs['int']
                elif t == loma_ir.Float():
                    return diff_structs['float']
                elif t == loma_ir.Struct():
                    return diff_structs[t.id]
                else:
                    # TODO: throw an user error
                    assert False, "No Diff[Array]"

    class DiffTypeMutator(irmutator.IRMutator):
        def mutate_function_def(self, node):
            new_args = [\
                loma_ir.Arg(arg.id, _replace_diff_type(arg.t), arg.i) \
                for arg in node.args]
            new_body = [self.mutate_stmt(stmt) for stmt in node.body]
            new_body = irmutator.flatten(new_body)
            return loma_ir.FunctionDef(\
                node.id,
                new_args,
                new_body,
                node.is_simd,
                _replace_diff_type(node.ret_type),
                lineno = node.lineno)

        def mutate_declare(self, dec):
            return loma_ir.Declare(\
                dec.target,
                _replace_diff_type(dec.t),
                self.mutate_expr(dec.val) if dec.val is not None else None,
                lineno = dec.lineno)

    return DiffTypeMutator().mutate_function(func)

def forward_diff(diff_func_id,
                 structs,
                 funcs,
                 diff_structs,
                 func):
    # HW1 happens here. Modify the following IR mutators to perform
    # forward differentiation.

    # Turn all primal access to a primitive type (int or float) into '.val'
    class PrimalMutator(irmutator.IRMutator):
        def mutate_var(self, node):
            # HW1: TODO
            return super().mutate_var(node)

        def mutate_array_access(self, node):
            # HW1: TODO
            return super().mutate_array_access(node)

        def mutate_struct_access(self, node):
            # HW1: TODO
            return super().mutate_struct_access(node)

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

def resolve_diff_types(structs, funcs):
    funcs_to_be_diffed = False
    for f in funcs.values():
        if isinstance(f, loma_ir.ForwardDiff) or isinstance(f, loma_ir.ReverseDiff):
            funcs_to_be_diffed = True

    if not funcs_to_be_diffed:
        return structs, {}, funcs

    diff_structs = {}
    dfloat = loma_ir.Struct('_dfloat',
                            [loma_ir.MemberDef('val', loma_ir.Float()),
                             loma_ir.MemberDef('dval', loma_ir.Float())])
    assert dfloat.id not in structs
    diff_structs['float'] = dfloat

    dint = loma_ir.Struct('_dint',
                          [loma_ir.MemberDef('val', loma_ir.Int())])
    assert dint.id not in structs
    diff_structs['int'] = dint

    def convert_struct_to_diff(s):
        match s:
            case loma_ir.Float():
                return dfloat
            case loma_ir.Int():
                return dint
            case loma_ir.Array():
                return loma_ir.Array(\
                    convert_struct_to_diff(s.t), s.static_size)
            case loma_ir.Struct():
                return loma_ir.Struct('_d' + s.id,
                    [loma_ir.MemberDef(m.id, convert_struct_to_diff(m.t)) for m in s.members])
            case _:
                assert False

    for s in structs.values():
        diff_structs[s.id] = convert_struct_to_diff(s)

    for ds in diff_structs.values():
        structs[ds.id] = ds

    # Replace all Diff types with their differential types in the code
    for f in funcs.values():
        funcs[f.id] = replace_diff_types(diff_structs, f)

    return structs, diff_structs, funcs

def differentiate(structs, diff_structs, funcs):
    funcs_to_be_diffed = False
    for f in funcs.values():
        if isinstance(f, loma_ir.ForwardDiff) or isinstance(f, loma_ir.ReverseDiff):
            funcs_to_be_diffed = True

    if not funcs_to_be_diffed:
        return structs, funcs

    for f in funcs.values():
        if isinstance(f, loma_ir.ForwardDiff):
            fwd_diff_func = forward_diff(\
                f.id, structs, funcs, diff_structs, funcs[f.primal_func])
            funcs[f.id] = fwd_diff_func

    return structs, funcs
