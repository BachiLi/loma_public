import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class IRVisitor:
    def visit_function(self, node):
        for stmt in node.body:
            self.visit_stmt(stmt)

    def visit_stmt(self, stmt):
        match stmt:
            case loma_ir.Return():
                self.visit_return(stmt)
            case loma_ir.Declare():
                self.visit_declare(stmt)
            case loma_ir.Assign():
                self.visit_assign(stmt)
            case loma_ir.IfElse():
                self.visit_ifelse(stmt)
            case loma_ir.While():
                self.visit_while(stmt)
            case _:
                assert False, f'Visitor error: unhandled statement {stmt}'

    def visit_return(self, ret):
        self.visit_expr(ret.val)

    def visit_declare(self, dec):
        self.visit_expr(dec.val)

    def visit_assign(self, ass):
        self.visit_expr(ass.val)

    def visit_ifelse(self, ifelse):
        self.visit_expr(ifelse.cond)
        for stmt in ifelse.then_stmts:
            self.visit_stmt(stmt)
        for stmt in ifelse.else_stmts:
            self.visit_stmt(stmt)

    def visit_while(self, while_loop):
        self.visit_expr(while_loop.cond)
        for stmt in while_loop.body:
            self.visit_stmt(stmt)

    def visit_expr(self, expr):
        match expr:
            case loma_ir.Var():
                self.visit_var(expr)
            case loma_ir.ArrayAccess():
                self.visit_array_access(expr)
            case loma_ir.StructAccess():
                self.visit_struct_access(expr)
            case loma_ir.ConstFloat():
                self.visit_const_float(expr)
            case loma_ir.ConstInt():
                self.visit_const_int(expr)
            case loma_ir.Add():
                self.visit_add(expr)
            case loma_ir.Sub():
                self.visit_sub(expr)
            case loma_ir.Mul():
                self.visit_mul(expr)
            case loma_ir.Div():
                self.visit_div(expr)
            case loma_ir.Compare():
                self.visit_compare(expr)
            case loma_ir.Call():
                self.visit_call(expr)
            case _:
                assert False, f'Visitor error: unhandled expression {expr}'

    def visit_var(self, var):
        pass

    def visit_array_access(self, acc):
        self.visit_ref(acc.array)
        self.visit_expr(acc.index)

    def visit_struct_access(self, s):
        self.visit_ref(s.struct)
        pass

    def visit_const_float(self, con):
        pass

    def visit_const_int(self, con):
        pass

    def visit_add(self, add):
        self.visit_expr(add.left)
        self.visit_expr(add.right)

    def visit_sub(self, sub):
        self.visit_expr(sub.left)
        self.visit_expr(sub.right)

    def visit_mul(self, mul):
        self.visit_expr(mul.left)
        self.visit_expr(mul.right)

    def visit_div(self, div):
        self.visit_expr(div.left)
        self.visit_expr(div.right)

    def visit_compare(self, cmp):
        self.visit_expr(cmp.left)
        self.visit_expr(cmp.right)

    def visit_call(self, call):
        for arg in call.args:
            self.visit_expr(arg)

    def visit_ref(self, ref):
        match ref:
            case loma_ir.RefName():
                self.visit_ref_name(ref)
            case loma_ir.RefArray():
                self.visit_ref_array(ref)
            case loma_ir.RefStruct():
                self.visit_ref_struct(ref)
            case _:
                assert False, f'Visitor error: unhandled ref {ref}'

    def visit_ref_name(self, ref):
        pass

    def visit_ref_array(self, ref):
        self.visit_ref(ref.array)
        self.visit_expr(ref.index)

    def visit_ref_struct(self, ref):
        self.visit_ref(ref.struct)
