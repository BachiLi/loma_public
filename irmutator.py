import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import itertools

def flatten(nested_list : list):
    # recursively flatten a nested list
    if len(nested_list) == 0:
        return nested_list
    if isinstance(nested_list[0], list):
        return flatten(nested_list[0]) + flatten(nested_list[1:])
    else:
        return nested_list[:1] + flatten(nested_list[1:])

class IRMutator:
    """ Visitor pattern: we use IRMutator to take a loma IR code,
        and mutate the code into something else. 
        To use this class, you should inherit IRMutator, and define
        your own mutate functions to do the transform.
        By default the class does nothing to the IR code.

        Note that during mutations of a statement,
        you can return multiple statements as a list.
        The other part of the code should handle the case
        when the returned statement is a list.
    """

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
        # Important: mutate_stmt can return a list of statements. We need to flatten the list.
        new_body = flatten(new_body)
        return loma_ir.FunctionDef(\
            node.id, node.args, new_body, node.is_simd, node.ret_type, lineno = node.lineno)

    def mutate_forward_diff(self, node):
        return node

    def mutate_reverse_diff(self, node):
        return node

    def mutate_stmt(self, node):
        match node:
            case loma_ir.Return():
                return self.mutate_return(node)
            case loma_ir.Declare():
                return self.mutate_declare(node)
            case loma_ir.Assign():
                return self.mutate_assign(node)
            case loma_ir.IfElse():
                return self.mutate_ifelse(node)
            case loma_ir.While():
                return self.mutate_while(node)
            case loma_ir.CallStmt():
                return self.mutate_call_stmt(node)
            case _:
                assert False, f'Visitor error: unhandled statement {node}'

    def mutate_return(self, node):
        return loma_ir.Return(\
            self.mutate_expr(node.val),
            lineno = node.lineno)

    def mutate_declare(self, node):
        return loma_ir.Declare(\
            node.target,
            node.t,
            self.mutate_expr(node.val) if node.val is not None else None,
            lineno = node.lineno)

    def mutate_assign(self, node):
        return loma_ir.Assign(\
            self.mutate_expr(node.target),
            self.mutate_expr(node.val),
            lineno = node.lineno)

    def mutate_ifelse(self, node):
        new_cond = self.mutate_expr(node.cond)
        new_then_stmts = [self.mutate_stmt(stmt) for stmt in node.then_stmts]
        new_else_stmts = [self.mutate_stmt(stmt) for stmt in node.else_stmts]
        # Important: mutate_stmt can return a list of statements. We need to flatten the lists.
        new_then_stmts = flatten(new_then_stmts)
        new_else_stmts = flatten(new_else_stmts)
        return loma_ir.IfElse(\
            new_cond,
            new_then_stmts,
            new_else_stmts,
            lineno = node.lineno)

    def mutate_while(self, node):
        new_cond = self.mutate_expr(node.cond)
        new_body = [self.mutate_stmt(stmt) for stmt in node.body]
        # Important: mutate_stmt can return a list of statements. We need to flatten the list.
        new_body = flatten(new_body)
        return loma_ir.While(\
            new_cond,
            node.max_iter,
            new_body,
            lineno = node.lineno)

    def mutate_call_stmt(self, node):
        return loma_ir.CallStmt(\
            self.mutate_expr(node.call),
            lineno = node.lineno)

    def mutate_expr(self, node):
        match node:
            case loma_ir.Var():
                return self.mutate_var(node)
            case loma_ir.ArrayAccess():
                return self.mutate_array_access(node)
            case loma_ir.StructAccess():
                return self.mutate_struct_access(node)
            case loma_ir.ConstFloat():
                return self.mutate_const_float(node)
            case loma_ir.ConstInt():
                return self.mutate_const_int(node)
            case loma_ir.BinaryOp():
                return self.mutate_binary_op(node)
            case loma_ir.Call():
                return self.mutate_call(node)
            case _:
                assert False, f'Visitor error: unhandled expression {node}'

    def mutate_var(self, node):
        return node

    def mutate_array_access(self, node):
        return loma_ir.ArrayAccess(\
            self.mutate_expr(node.array),
            self.mutate_expr(node.index),
            lineno = node.lineno,
            t = node.t)

    def mutate_struct_access(self, node):
        return loma_ir.StructAccess(\
            self.mutate_expr(node.struct),
            node.member_id,
            lineno = node.lineno,
            t = node.t)

    def mutate_const_float(self, node):
        return node

    def mutate_const_int(self, node):
        return node

    def mutate_binary_op(self, node):
        match node.op:
            case loma_ir.Add():
                return self.mutate_add(node)
            case loma_ir.Sub():
                return self.mutate_sub(node)
            case loma_ir.Mul():
                return self.mutate_mul(node)
            case loma_ir.Div():
                return self.mutate_div(node)
            case loma_ir.Less():
                return self.mutate_less(node)
            case loma_ir.LessEqual():
                return self.mutate_less_equal(node)
            case loma_ir.Greater():
                return self.mutate_greater(node)
            case loma_ir.GreaterEqual():
                return self.mutate_greater_equal(node)
            case loma_ir.Equal():
                return self.mutate_equal(node)
            case loma_ir.And():
                return self.mutate_and(node)
            case loma_ir.Or():
                return self.mutate_or(node)

    def mutate_add(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Add(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_sub(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Sub(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_mul(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Mul(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_div(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Div(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_less(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Less(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_less_equal(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.LessEqual(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_greater(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Greater(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_greater_equal(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.GreaterEqual(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_equal(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Equal(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_and(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.And(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_or(self, node):
        return loma_ir.BinaryOp(\
            loma_ir.Or(),
            self.mutate_expr(node.left),
            self.mutate_expr(node.right),
            lineno = node.lineno,
            t = node.t)

    def mutate_call(self, node):
        return loma_ir.Call(\
            node.id,
            [self.mutate_expr(arg) for arg in node.args],
            lineno = node.lineno,
            t = node.t)
