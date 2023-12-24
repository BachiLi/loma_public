class IRVisitor:
    def visit_function(self, node):
        self.visit_block(node)

    def visit_block(self, node):
        for stmt in node.s:
            self.emit_stmt(stmt)

    def visit_stmt(self, stmt):
        if isinstance(stmt, loma_ir.Return):
            self.visit_return(stmt)
        elif isinstance(stmt, loma_ir.Declare):
            self.visit_declare(stmt)
        else:
            assert False, f'Visitor error: unhandled statement {stmt}'

    def visit_return(self, ret):
        self.visit(ret.val)

    def visit_declare(self, dec):
        self.visit(dec.val)

    def visit_expr(self, expr):
        if isinstance(expr, loma_ir.Var):
            self.visit_var()
        elif isinstance(expr, loma_ir.Const):
            self.visit_const()
        elif isinstance(expr, loma_ir.Add):
            self.visit_add()
        elif isinstance(expr, loma_ir.Sub):
            self.visit_sub()
        elif isinstance(expr, loma_ir.Mul):
            self.visit_mul()
        elif isinstance(expr, loma_ir.Div):
            self.visit_div()
        else:
            assert False, f'Visitor error: unhandled expression {expr}'

    def visit_var(self, var):
        pass

    def visit_const(self, con):
        pass

    def visit_add(self, add):
        pass

    def visit_sub(self, sub):
        pass

    def visit_mul(self, mul):
        pass

    def visit_div(self, div):
        pass
