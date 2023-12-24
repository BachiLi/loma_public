import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class IRVisitor:
    def visit_function(self, node):
        for stmt in node.body:
            self.visit_stmt(stmt)

    def visit_stmt(self, stmt):
        if isinstance(stmt, loma_ir.Return):
            self.visit_return(stmt)
        elif isinstance(stmt, loma_ir.Declare):
            self.visit_declare(stmt)
        else:
            assert False, f'Visitor error: unhandled statement {stmt}'

    def visit_return(self, ret):
        self.visit_expr(ret.val)

    def visit_declare(self, dec):
        self.visit_expr(dec.val)

    def visit_expr(self, expr):
        if isinstance(expr, loma_ir.Var):
            self.visit_var(expr)
        elif isinstance(expr, loma_ir.Const):
            self.visit_const(expr)
        elif isinstance(expr, loma_ir.Add):
            self.visit_add(expr)
        elif isinstance(expr, loma_ir.Sub):
            self.visit_sub(expr)
        elif isinstance(expr, loma_ir.Mul):
            self.visit_mul(expr)
        elif isinstance(expr, loma_ir.Div):
            self.visit_div(expr)
        else:
            assert False, f'Visitor error: unhandled expression {expr}'

    def visit_var(self, var):
        pass

    def visit_const(self, con):
        pass

    def visit_add(self, add):
        visit_expr(add.left)
        visit_expr(add.right)

    def visit_sub(self, sub):
        visit_expr(add.left)
        visit_expr(add.right)

    def visit_mul(self, mul):
        visit_expr(add.left)
        visit_expr(add.right)

    def visit_div(self, div):
        visit_expr(add.left)
        visit_expr(add.right)
