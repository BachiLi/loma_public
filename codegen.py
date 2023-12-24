import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def codegen(func):
    class Codegen:
        def __init__(self):
            self.code = ''
            self.tab_count = 0

        def emit_tabs(self):
            self.code += '\t' * self.tab_count

        def emit_function(self, node):
            self.code += f'extern \"C\" float {node.name}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'float {arg}'
            self.code += ') {\n'
            self.tab_count += 1
            self.emit_block(node.body)
            self.tab_count -= 1
            self.code += '}\n'        

        def emit_block(self, node):
            for stmt in node.s:
                self.emit_stmt(stmt)

        def emit_stmt(self, stmt):
            if isinstance(stmt, loma_ir.Return):
                self.emit_tabs()
                self.code += f'return {self.get_expr_str(stmt.val)};\n'
            elif isinstance(stmt, loma_ir.Declare):
                self.emit_tabs()
                self.code += f'float {stmt.target} = {self.get_expr_str(stmt.val)};\n'
            else:
                assert False, f'Codegen error: unhandled statement {stmt}'

        def get_expr_str(self, expr):
            if isinstance(expr, loma_ir.Var):
                return expr.id
            elif isinstance(expr, loma_ir.Const):
                return expr.val
            elif isinstance(expr, loma_ir.Add):
                return f'({self.get_expr_str(expr.left)}) + ({self.get_expr_str(expr.right)})'
            elif isinstance(expr, loma_ir.Sub):
                return f'({self.get_expr_str(expr.left)}) - ({self.get_expr_str(expr.right)})'
            elif isinstance(expr, loma_ir.Mul):
                return f'({self.get_expr_str(expr.left)}) * ({self.get_expr_str(expr.right)})'
            elif isinstance(expr, loma_ir.Div):
                return f'({self.get_expr_str(expr.left)}) / ({self.get_expr_str(expr.right)})'
            else:
                assert False, f'Codegen error: unhandled expression {expr}'

    cg = Codegen()
    cg.emit_function(func)
    return cg.code
