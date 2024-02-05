import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

class IRMutator:
    def mutate_function(self, node):
        match node:
            case loma_ir.FunctionDef():
                return self.mutate_function_def(node)
            case loma_ir.ForwardDiff():
                return self.mutate_forward_diff(node)
            case loma_ir.ReverseDiff():
                return self.mutate_reverse_diff(node)
            case _:
                assert False, f'Visitor error: unhandled func {node}'

    def mutate_function_def(self, node):
        new_body = [self.mutate_stmt(stmt) for stmt in node.body]
        return loma_ir.FunctionDef(\
            node.id, node.args, new_body, node.is_simd, node.ret_type, lineno = node.lineno)

    def mutate_forward_diff(self, node):
        return node

    def mutate_reverse_diff(self, node):
        return node

    def mutate_stmt(self, stmt):
        match stmt:
            case loma_ir.Return():
                return self.mutate_return(stmt)
            case loma_ir.Declare():
                return self.mutate_declare(stmt)
            case loma_ir.Assign():
                return self.mutate_assign(stmt)
            case loma_ir.IfElse():
                return self.mutate_ifelse(stmt)
            case loma_ir.While():
                return self.mutate_while(stmt)
            case _:
                assert False, f'Visitor error: unhandled statement {stmt}'

    def mutate_return(self, ret):
        return loma_ir.Return(\
            self.mutate_expr(ret.val),
            lineno = ret.lineno)

    def visit_declare(self, dec):
        return loma_ir.Declare(\
            dec.target,
            dec.t,
            self.mutate_expr(dec.val),
            lineno = dec.lineno)

    def visit_assign(self, ass):
        return loma_ir.Assign(\
            ass.target,
            self.mutate_expr(ass.val),
            lineno = ass.lineno)

    def visit_ifelse(self, ifelse):
        new_cond = self.mutate_expr(ifelse.cond)
        new_then_stmts = [self.mutate_stmt(stmt) for stmt in ifelse.then_stmts]
        new_else_stmts = [self.mutate_stmt(stmt) for stmt in ifelse.else_stmts]
        return loma_ir.IfElse(\
            new_cond,
            new_then_stmts,
            new_else_stmts,
            lineno = ifelse.lineno)

    def visit_while(self, while_loop):
        new_cond = self.mutate_expr(while_loop.cond)
        new_body = [self.mutate_stmt(stmt) for stmt in while_loop.body]
        return loma_ir.While(\
            new_cond,
            new_body,
            lineno = while_loop.lineno)

    def visit_expr(self, expr):
        match expr:
            case loma_ir.Var():
                return self.mutate_var(expr)
            case loma_ir.ArrayAccess():
                return self.mutate_array_access(expr)
            case loma_ir.StructAccess():
                return self.mutate_struct_access(expr)
            case loma_ir.ConstFloat():
                return self.mutate_const_float(expr)
            case loma_ir.ConstInt():
                return self.mutate_const_int(expr)
            case loma_ir.BinaryOp():
                return self.mutate_binary_op(expr)
            case loma_ir.Call():
                return self.mutate_call(expr)
            case _:
                assert False, f'Visitor error: unhandled expression {expr}'

    def mutate_var(self, var):
        return var

    def mutate_array_access(self, acc):
        return loma_ir.ArrayAccess(\
            self.mutate_ref(acc.array),
            self.mutate_expr(acc.index),
            lineno = acc.lineno,
            t = acc.t)

    def mutate_struct_access(self, s):
        return loma_ir.StructAccess(\
            self.mutate_ref(s.struct),
            s.member_id,
            lineno = acc.lineno,
            t = s.t)

    def mutate_const_float(self, con):
        return con

    def mutate_const_int(self, con):
        return con

    def mutate_binary_op(self, expr):
        match expr.op:
            case loma_ir.Add():
                return self.mutate_add(expr)
            case loma_ir.Sub():
                return self.mutate_sub(expr)
            case loma_ir.Mul():
                return self.mutate_mul(expr)
            case loma_ir.Div():
                return self.mutate_div(expr)
            case loma_ir.Less():
                return self.mutate_less(expr)
            case loma_ir.LessEqual():
                return self.mutate_less_equal(expr)
            case loma_ir.Greater():
                return self.mutate_greater(expr)
            case loma_ir.GreaterEqual():
                return self.mutate_greater_equal(expr)
            case loma_ir.Equal():
                return self.mutate_equal(expr)
            case loma_ir.And():
                return self.mutate_and(expr)
            case loma_ir.Or():
                return self.mutate_or(expr)

    def mutate_add(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Add(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_sub(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Sub(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_mul(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Mul(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_div(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Div(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_less(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Less(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_less_equal(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.LessEqual(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_greater(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Greater(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_greater_equal(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.GreaterEqual(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_equal(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Equal(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_and(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.And(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_or(self, expr):
        return loma_ir.BinaryOp(\
            loma_ir.Or(),
            self.mutate_expr(expr.left),
            self.mutate_expr(expr.right),
            lineno = expr.lineno,
            t = expr.t)

    def mutate_call(self, call):
        return loma_ir.Call(\
            call.id,
            [self.mutate_expr(arg) for arg in call.args],
            lineno = call.lineno,
            t = call.t)

    def mutate_ref(self, ref):
        match ref:
            case loma_ir.RefName():
                return self.mutate_ref_name(ref)
            case loma_ir.RefArray():
                return self.mutate_ref_array(ref)
            case loma_ir.RefStruct():
                return self.mutate_ref_struct(ref)
            case _:
                assert False, f'Visitor error: unhandled ref {ref}'

    def mutate_ref_name(self, ref):
        return ref

    def mutate_ref_array(self, ref):
        return loma_ir.RefArray(\
            self.mutate_ref(ref.array),
            self.mutate_expr(ref.index))

    def mutate_ref_struct(self, ref):
        return loma_ir.RefStruct(\
            self.mutate_ref(ref.struct),
            ref.member)
        
