import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class IRVisitor:
    def visit_function(self, node):
        match node:
            case loma_ir.FunctionDef():
                self.visit_function_def(node)
            case loma_ir.ForwardDiff():
                self.visit_forward_diff(node)
            case loma_ir.ReverseDiff():
                self.visit_reverse_diff(node)
            case _:
                assert False, f'Visitor error: unhandled func {node}'

    def visit_function_def(self, node):
        for stmt in node.body:
            self.visit_stmt(stmt)

    def visit_forward_diff(self, node):
        pass

    def visit_reverse_diff(self, node):
        pass

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
        if dec.val is not None:
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
            case loma_ir.BinaryOp():
                self.visit_binary_op(expr)
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

    def visit_binary_op(self, expr):
        match expr.op:
            case loma_ir.Add():
                self.visit_add(expr)
            case loma_ir.Sub():
                self.visit_sub(expr)
            case loma_ir.Mul():
                self.visit_mul(expr)
            case loma_ir.Div():
                self.visit_div(expr)
            case loma_ir.Less():
                self.visit_less(expr)
            case loma_ir.LessEqual():
                self.visit_less_equal(expr)
            case loma_ir.Greater():
                self.visit_greater(expr)
            case loma_ir.GreaterEqual():
                self.visit_greater_equal(expr)
            case loma_ir.Equal():
                self.visit_equal(expr)
            case loma_ir.And():
                self.visit_and(expr)
            case loma_ir.Or():
                self.visit_or(expr)

    def visit_add(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_sub(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_mul(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_div(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_less(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_less_equal(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_greater(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_greater_equal(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_equal(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_and(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

    def visit_or(self, expr):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)

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
