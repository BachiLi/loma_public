import codegen_c
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class OpenCLCodegenVisitor(codegen_c.CCodegenVisitor):
    """ Generates OpenCL code from loma IR.
    """

    def visit_function_def(self, node):
        if node.is_simd:
            self.code += f'__kernel void {node.id}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'__global {codegen_c.type_to_string(arg.t)} {arg.id}'
            self.code += ') {\n'
        else:
            self.code += f'{codegen_c.type_to_string(node.ret_type)} {node.id}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'{codegen_c.type_to_string(arg.t)} {arg.id}'
            self.code += ') {\n'

        self.tab_count += 1
        for stmt in node.body:
            self.visit_stmt(stmt)

        self.tab_count -= 1
        self.emit_tabs()
        self.code += '}\n'

    def visit_expr(self, expr):
        match expr:
            case loma_ir.Call():
                if expr.id == 'thread_id':
                    return 'get_global_id(0)'
                else:
                    return super().visit_expr(expr)
            case _:
                return super().visit_expr(expr)



def codegen_opencl(structs : dict[str, loma_ir.Struct],
                   funcs : dict[str, loma_ir.func]) -> str:
    """ Given loma Structs (structs) and loma functions (funcs),
        return a string that represents the equivalent OpenCL code.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
    """

    # Sort the struct topologically
    sorted_structs_list = []
    traversed_struct = set()
    def traverse_structs(s):
        if s in traversed_struct:
            return
        for m in s.members:
            if isinstance(m.t, loma_ir.Struct) or isinstance(m.t, loma_ir.Array):
                next_s = m.t if isinstance(m.t, loma_ir.Struct) else m.t.t
                if isinstance(next_s, loma_ir.Struct):
                    traverse_structs(structs[next_s.id])
        sorted_structs_list.append(s)
        traversed_struct.add(s)
    for s in structs.values():
        traverse_structs(s)

    # Definition of structs
    code = ''
    for s in sorted_structs_list:
        code += f'typedef struct {s.id} {{\n'
        for m in s.members:
            code += f'\t{codegen_c.type_to_string(m.t)} {m.id};\n'
        code += f'}} {s.id};\n'

    # Forward declaration of functions
    for f in funcs.values():
        if f.is_simd:
            code += '__kernel '
        code += f'{codegen_c.type_to_string(f.ret_type)} {f.id}('
        for i, arg in enumerate(f.args):
            if i > 0:
                code += ', '
            if f.is_simd:
                code += '__global '
            code += f'{codegen_c.type_to_string(arg.t)}'
            code += f' {arg.id}'
        code += ');\n'

    for f in funcs.values():
        cg = OpenCLCodegenVisitor()
        cg.visit_function(f)
        code += cg.code

    return code
