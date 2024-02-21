import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irmutator
import forward_diff

def replace_diff_types(diff_structs : dict[str, loma_ir.Struct],
                       func : loma_ir.FunctionDef) -> loma_ir.FunctionDef:
    """ Given a loma function func, find all function arguments and
        declarations with type Diff[...] and turn them into the 
        corresponding differential type by looking up diff_structs.

        For example, the following loma code
        x : Diff[float]
        will be turned into
        x : _dfloat

        where _dfloat is
        class _dfloat:
            val : float
            dval : float

        diff_structs is a map that goes from the ID of the type to the 
        differential struct. For example, diff_structs['float'] will 
        return the _dfloat type.

        Currently, we do not allow repeated applications of Diff[]
        (like Diff[Diff[float]]).
    """

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
                if isinstance(t, loma_ir.Int):
                    return diff_structs['int']
                elif isinstance(t, loma_ir.Float):
                    return diff_structs['float']
                elif isinstance(t, loma_ir.Struct):
                    return diff_structs[t.id]
                else:
                    # TODO: throw an user error
                    assert False, "No Diff[Array]"

    class DiffTypeMutator(irmutator.IRMutator):
        def mutate_function_def(self, node):
            new_args = [\
                loma_ir.Arg(arg.id, _replace_diff_type(arg.t), arg.is_byref) \
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

        def mutate_declare(self, node):
            return loma_ir.Declare(\
                node.target,
                _replace_diff_type(node.t),
                self.mutate_expr(node.val) if node.val is not None else None,
                lineno = node.lineno)

    return DiffTypeMutator().mutate_function(func)

def resolve_diff_types(structs : dict[str, loma_ir.Struct],
                       funcs : dict[str, loma_ir.func]) -> \
        tuple[dict[str, loma_ir.Struct], dict[str, loma_ir.Struct], dict[str, loma_ir.func]]:
    """ Given a list of primal loma Struct (structs) and functions (funcs),
        generate a list of the corresponding differential Structs,
        and resolve all the Diff[] types in the functions.

        Firstly, the following two differential structs are created
        for the primitive types int and float:
        class _dint:
            val : int
        class _dfloat:
            val : float
            dval : float

        Next, for each Struct in structs, we convert them by recursively applying
        the differentiation to each of the member. For example, the following primal Struct
        class Foo:
            x : float
            y : int
        will be converted to
        class _dFoo:
            x : _dfloat
            y : _dint
        and the following primal Struct
        class Bar:
            z : Foo
        will be converted to
        class _dBar:
            z : _dFoo

        The naming of the differential Structs is done by prefixing '_d' to the struct ID.

        Next, we go through all functions in funcs, and resolve the Diff[] types.
        See replace_diff_types() for more details.

        resolve_diff_types returns three dictionaries:
        - structs: it now includes not just all the primal Structs, but all the differential Structs
        - diff_structs: maps from the primal Struct ID to the differential Struct
        - funcs: all the primal funcs with Diff[] types resolved
    """

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

def differentiate(structs : dict[str, loma_ir.Struct],
                  diff_structs : dict[str, loma_ir.Struct],
                  funcs : dict[str, loma_ir.func]) -> dict[str, loma_ir.func]:
    """ Given a list loma functions (funcs), replace all functions 
        that are marked as ForwardDiff and ReverseDiff with 
        FunctionDef and the actual implementations.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        diff_structs - a dictionary that maps the ID of the primal
                Struct to the corresponding differential Struct
                e.g., diff_structs['float'] returns _dfloat
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func

        Returns:
        funcs - now all functions that are ForwardDiff and ReverseDiff
                are replaced by the actual FunctionDef
    """

    funcs_to_be_diffed = False
    for f in funcs.values():
        if isinstance(f, loma_ir.ForwardDiff) or isinstance(f, loma_ir.ReverseDiff):
            funcs_to_be_diffed = True

    if not funcs_to_be_diffed:
        return funcs

    for f in funcs.values():
        if isinstance(f, loma_ir.ForwardDiff):
            fwd_diff_func = forward_diff.forward_diff(\
                f.id, structs, funcs, diff_structs, funcs[f.primal_func])
            funcs[f.id] = fwd_diff_func
        elif isinstance(f, loma_ir.ReverseDiff):
            assert False

    return funcs
