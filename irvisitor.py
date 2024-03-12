import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class IRVisitor:
    """ Visitor pattern: we use IRVisitor to traverse loma IR code,
        and visit its children.
        To use this class, you should inherit IRVisitor, and define
        your own visit functions to decide what to do.
        By default the class does nothing to the IR code.
    """

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

    def visit_stmt(self, node):
        match node:
            case loma_ir.Return():
                self.visit_return(node)
            case loma_ir.Declare():
                self.visit_declare(node)
            case loma_ir.Assign():
                self.visit_assign(node)
            case loma_ir.IfElse():
                self.visit_ifelse(node)
            case loma_ir.While():
                self.visit_while(node)
            case loma_ir.CallStmt():
                self.visit_call_stmt(node)
            case _:
                assert False, f'Visitor error: unhandled statement {node}'

    def visit_return(self, node):
        self.visit_expr(node.val)

    def visit_declare(self, node):
        if node.val is not None:
            self.visit_expr(node.val)

    def visit_assign(self, node):
        self.visit_expr(node.val)

    def visit_ifelse(self, node):
        self.visit_expr(node.cond)
        for stmt in node.then_stmts:
            self.visit_stmt(stmt)
        for stmt in node.else_stmts:
            self.visit_stmt(stmt)

    def visit_while(self, node):
        self.visit_expr(node.cond)
        for stmt in node.body:
            self.visit_stmt(stmt)

    def visit_call_stmt(self, node):
        self.visit_expr(node.call)

    def visit_expr(self, node):
        match node:
            case loma_ir.Var():
                self.visit_var(node)
            case loma_ir.ArrayAccess():
                self.visit_array_access(node)
            case loma_ir.StructAccess():
                self.visit_struct_access(node)
            case loma_ir.ConstFloat():
                self.visit_const_float(node)
            case loma_ir.ConstInt():
                self.visit_const_int(node)
            case loma_ir.BinaryOp():
                self.visit_binary_op(node)
            case loma_ir.Call():
                self.visit_call(node)
            case _:
                assert False, f'Visitor error: unhandled expression {node}'

    def visit_var(self, node):
        pass

    def visit_array_access(self, node):
        self.visit_expr(node.array)
        self.visit_expr(node.index)

    def visit_struct_access(self, node):
        self.visit_expr(node.struct)
        pass

    def visit_const_float(self, node):
        pass

    def visit_const_int(self, node):
        pass

    def visit_binary_op(self, node):
        match node.op:
            case loma_ir.Add():
                self.visit_add(node)
            case loma_ir.Sub():
                self.visit_sub(node)
            case loma_ir.Mul():
                self.visit_mul(node)
            case loma_ir.Div():
                self.visit_div(node)
            case loma_ir.Less():
                self.visit_less(node)
            case loma_ir.LessEqual():
                self.visit_less_equal(node)
            case loma_ir.Greater():
                self.visit_greater(node)
            case loma_ir.GreaterEqual():
                self.visit_greater_equal(node)
            case loma_ir.Equal():
                self.visit_equal(node)
            case loma_ir.And():
                self.visit_and(node)
            case loma_ir.Or():
                self.visit_or(node)

    def visit_add(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_sub(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_mul(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_div(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_less(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_less_equal(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_greater(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_greater_equal(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_equal(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_and(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_or(self, node):
        self.visit_expr(node.left)
        self.visit_expr(node.right)

    def visit_call(self, node):
        for arg in node.args:
            self.visit_expr(arg)
