import codegen_c
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import compiler

def type_to_string(node : loma_ir.type | loma_ir.arg) -> str:
    """ Given a loma type, return a string that represents
        the type in C.
    """

    match node:
        case loma_ir.Arg():
            if isinstance(node.t, loma_ir.Array):
                if node.i == loma_ir.In():
                    return f'StructuredBuffer<{type_to_string(node.t.t)}>'
                else:
                    return f'RWStructuredBuffer<{type_to_string(node.t.t)}>'
            elif node.i == loma_ir.Out():
                return f'RWStructuredBuffer<{type_to_string(node.t)}>'
            else:
                return type_to_string(node.t)
        case loma_ir.Int():
            return 'int'
        case loma_ir.Float():
            return 'float'
        case loma_ir.Array():
            if node.static_size != None:
                return type_to_string(node.t) + f'[{node.static_size}]'
            else:
                return type_to_string(node.t) + '[]'
        case loma_ir.Struct():
            return node.id
        case None:
            return 'void'
        case _:
            assert False

class SlangCodegenVisitor(codegen_c.CCodegenVisitor):
    """ Generates Slang compute shader code from loma IR.
    """

    def __init__(self, func_defs):
        super().__init__(func_defs)

    def visit_function_def(self, node):
        if node.is_simd:
            self.code += '[shader(\"compute\")]\n'
            self.code += '[numthreads(64, 1, 1)]\n'
            self.code += f'void {node.id}('
            self.code += 'uint _tid: SV_DispatchThreadID, '
            self.code += 'uniform int _total_threads'
            for i, arg in enumerate(node.args):
                self.code += ', '
                if not isinstance(arg.t, loma_ir.Array):
                    self.code += 'uniform '
                self.code += f'{type_to_string(arg)} {arg.id}'
            self.code += ') {\n'
        else:
            self.code += f'{type_to_string(node.ret_type)} {node.id}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'{type_to_string(arg)} {arg.id}'
            self.code += ') {\n'

        self.byref_args = set([arg.id for arg in node.args if \
            arg.i == loma_ir.Out() and (not isinstance(arg.t, loma_ir.Array))])

        self.tab_count += 1
        self.code += '\tif (_tid >= _total_threads) return;\n'
        for stmt in node.body:
            self.visit_stmt(stmt)

        self.tab_count -= 1
        self.emit_tabs()
        self.code += '}\n'

    def visit_expr(self, node):
        match node:
            case loma_ir.Call():
                if node.id == 'thread_id':
                    return '_tid'
                elif node.id == 'atomic_add':
                    assert False
        return super().visit_expr(node)

def codegen_slang(structs : dict[str, loma_ir.Struct],
                  funcs : dict[str, loma_ir.func]) -> str:
    """ Given loma Structs (structs) and loma functions (funcs),
        return a string that represents the equivalent Slang code.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
    """

    sorted_structs_list = compiler.topo_sort_structs(structs)

    # Definition of structs
    code = ''
    for s in sorted_structs_list:
        code += f'struct {s.id} {{\n'
        for m in s.members:
            code += f'\t{codegen_c.type_to_string(m.t)} {m.id};\n'
        code += f'}} {s.id};\n'

    for f in funcs.values():
        cg = SlangCodegenVisitor(funcs)
        cg.visit_function(f)
        code += cg.code

    return code
