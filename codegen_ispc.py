import codegen_c
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class ISPCCodegenVisitor(codegen_c.CCodegenVisitor):
    """ Generates ISPC code from loma IR.
        See https://ispc.github.io/index.html for more details about ispc.
    """

    def visit_function_def(self, node):
        if node.is_simd:
            self.code += f'task void __{node.id}_task('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'uniform {codegen_c.type_to_string(arg.t)} uniform {arg.id}'
            if len(node.args) > 0:
                self.code += ', '
            self.code += 'uniform int total_work'
            self.code += ', uniform int work_per_task'
            self.code += ', uniform int task_index'
            self.code += ') {\n'

            self.tab_count += 1
            self.emit_tabs()
            self.code += 'uniform int id_offset = work_per_task * task_index;\n'
            self.emit_tabs()
            self.code += 'uniform int work_end = min(id_offset + work_per_task, total_work);\n'
            self.emit_tabs()
            self.code += 'foreach (__work_id = id_offset ... work_end) {\n'
            self.tab_count += 1

            for stmt in node.body:
                self.visit_stmt(stmt)

            self.tab_count -= 1
            self.emit_tabs()
            self.code += '}\n'

            self.tab_count -= 1
            self.emit_tabs()
            self.code += '}\n'

            self.code += f'export void {node.id}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'uniform {codegen_c.type_to_string(arg.t)} uniform {arg.id}'
            if len(node.args) > 0:
                self.code += ', '
            self.code += 'uniform int total_work'
            self.code += ') {\n'
            self.code += '\tuniform int num_tasks = num_cores() * 4;\n';
            self.code += '\tuniform int work_per_task = total_work / num_tasks;\n';
            self.code += '\tif (total_work % num_tasks != 0) work_per_task++;\n'
            self.code += '\tfor (uniform int task_index = 0; task_index < num_tasks; task_index++) {\n'
            self.code += f'\t\tlaunch __{node.id}_task('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += arg.id
            self.code += ', total_work, work_per_task, task_index);\n'
            self.code += '\t}\n'
            self.code += '\tsync;\n'
            self.code += '}\n'
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
            self.code += '}\n'

def codegen_ispc(structs : dict[str, loma_ir.Struct],
                 funcs : dict[str, loma_ir.func]) -> str:
    """ Given loma Structs (structs) and loma functions (funcs),
        return a string that represents the equivalent ISPC code.

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
        code += f'struct {s.id} {{\n'
        for m in s.members:
            code += f'\t{codegen_c.type_to_string(m.t)} {m.id};\n'
        code += f'}};\n'

    # Forward declaration of functions
    for f in funcs.values():
        if f.is_simd:
            code += 'export '
        code += f'{codegen_c.type_to_string(f.ret_type)} {f.id}('
        for i, arg in enumerate(f.args):
            if i > 0:
                code += ', '
            if f.is_simd:
                code += 'uniform '
            code += f'{codegen_c.type_to_string(arg.t)}'
            if f.is_simd:
                code += ' uniform'
            code += f' {arg.id}'
        if f.is_simd:
            if len(f.args) > 0:
                code += ', '
            code += 'uniform int total_work'
        code += ');\n'

    for f in funcs.values():
        cg = ISPCCodegenVisitor()
        cg.visit_function(f)
        code += cg.code

    return code
