import attrs
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import visitor

def codegen(func):

    @attrs.define()
    class CGVisitor(visitor.IRVisitor):
        code = ''
        tab_count = 0

        def emit_tabs(self):
            self.code += '\t' * self.tab_count

        def visit_function(self, node):
            self.code += f'extern \"C\" float {node.name}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'float {arg}'
            self.code += ') {\n'
            self.tab_count += 1
            for stmt in node.body:
                self.visit_stmt(stmt)
            self.tab_count -= 1
            self.code += '}\n'        

        def visit_return(self, ret):
            self.emit_tabs()
            self.code += f'return {self.visit_expr(ret.val)};\n'

        def visit_declare(self, dec):
            self.emit_tabs()
            self.code += f'float {dec.target} = {self.visit_expr(dec.val)};\n'

        def visit_assign(self, ass):
            self.emit_tabs()
            self.code += f'{ass.target} = {self.visit_expr(ass.val)};\n'

        def visit_expr(self, expr):
            if isinstance(expr, loma_ir.Var):
                return expr.id
            elif isinstance(expr, loma_ir.ConstFloat):
                return expr.val
            elif isinstance(expr, loma_ir.Add):
                return f'({self.visit_expr(expr.left)}) + ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Sub):
                return f'({self.visit_expr(expr.left)}) - ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Mul):
                return f'({self.visit_expr(expr.left)}) * ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Div):
                return f'({self.visit_expr(expr.left)}) / ({self.visit_expr(expr.right)})'
            else:
                assert False, f'Visitor error: unhandled expression {expr}'

    cg = CGVisitor()
    cg.visit_function(func)
    return cg.code
