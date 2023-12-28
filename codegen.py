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

        def type_to_string(self, node):
            if isinstance(node, loma_ir.Int):
                return 'int'
            elif isinstance(node, loma_ir.Float):
                return 'float'
            elif isinstance(node, loma_ir.Array):
                return self.type_to_string(node.t) + '*'
            elif node == None:
                return 'void'
            else:
                assert False

        def visit_function(self, node):
            self.code += f'extern \"C\" {self.type_to_string(node.ret_type)} {node.name}('
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.code += ', '
                self.code += f'{self.type_to_string(arg.t)} {arg.id}'
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
            self.code += f'{self.type_to_string(dec.t)} {dec.target} = {self.visit_expr(dec.val)};\n'

        def visit_assign(self, ass):
            self.emit_tabs()
            if ass.index is None:
                self.code += f'{ass.target} = {self.visit_expr(ass.val)};\n'
            else:
                self.code += f'{ass.target}[{self.visit_expr(ass.index)}] = {self.visit_expr(ass.val)};\n'

        def visit_ifelse(self, ifelse):
            self.emit_tabs()
            self.code += f'if ({self.visit_expr(ifelse.cond)}) {{\n'
            self.tab_count += 1
            for stmt in ifelse.then_stmts:
                self.visit_stmt(stmt)
            self.tab_count -= 1
            self.emit_tabs()
            self.code += f'}} else {{\n'
            self.tab_count += 1
            for stmt in ifelse.else_stmts:
                self.visit_stmt(stmt)
            self.tab_count -= 1
            self.emit_tabs()
            self.code += '}\n'

        def visit_expr(self, expr):
            if isinstance(expr, loma_ir.Var):
                return expr.id
            elif isinstance(expr, loma_ir.ArrayAccess):
                return f'{expr.id}[{self.visit_expr(expr.index)}]'
            elif isinstance(expr, loma_ir.ConstFloat):
                return f'(float)({expr.val})'
            elif isinstance(expr, loma_ir.ConstInt):
                return f'(int)({expr.val})'
            elif isinstance(expr, loma_ir.Add):
                return f'({self.visit_expr(expr.left)}) + ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Sub):
                return f'({self.visit_expr(expr.left)}) - ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Mul):
                return f'({self.visit_expr(expr.left)}) * ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Div):
                return f'({self.visit_expr(expr.left)}) / ({self.visit_expr(expr.right)})'
            elif isinstance(expr, loma_ir.Compare):
                if expr.op == loma_ir.Less():
                    return f'({self.visit_expr(expr.left)}) < ({self.visit_expr(expr.right)})'
                elif expr.op == loma_ir.LessEqual():
                    return f'({self.visit_expr(expr.left)}) <= ({self.visit_expr(expr.right)})'
                elif expr.op == loma_ir.Greater():
                    return f'({self.visit_expr(expr.left)}) > ({self.visit_expr(expr.right)})'
                elif expr.op == loma_ir.GreaterEqual():
                    return f'({self.visit_expr(expr.left)}) >= ({self.visit_expr(expr.right)})'
                elif expr.op == loma_ir.Equal():
                    return f'({self.visit_expr(expr.left)}) == ({self.visit_expr(expr.right)})'
                elif expr.op == loma_ir.And():
                    return f'({self.visit_expr(expr.left)}) && ({self.visit_expr(expr.right)})'
                elif expr.op == loma_ir.Or():
                    return f'({self.visit_expr(expr.left)}) || ({self.visit_expr(expr.right)})'
            else:
                assert False, f'Visitor error: unhandled expression {expr}'

    cg = CGVisitor()
    cg.visit_function(func)
    return cg.code
