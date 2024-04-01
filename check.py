import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import error
import irvisitor
import type_inference

def check_duplicate_declare(node : loma_ir.func):
    """ Check if there are duplicated declaration of variables in loma code.
        For example, the following loma code is illegal:
        x : float
        x : int

        If we find a duplicated declaration, raise an error.
    """

    class DuplicateChecker(irvisitor.IRVisitor):
        ids_stmt_map = {}

        def visit_function_def(self, node):
            for arg in node.args:
                if arg.id in self.ids_stmt_map:
                    raise error.DuplicateVariable(arg.id,
                                                  self.ids_stmt_map[arg.id],
                                                  arg)
                self.ids_stmt_map[arg.id] = arg
            for stmt in node.body:
                self.visit_stmt(stmt)

        def visit_declare(self, node):
            if node.target in self.ids_stmt_map:
                raise error.DuplicateVariable(node.target,
                                              self.ids_stmt_map[node.target],
                                              node)
            self.ids_stmt_map[node.target] = node

    DuplicateChecker().visit_function(node)

def check_undeclared_vars(node : loma_ir.func):
    """ Check if there are undeclared use variables in loma code.
        For example, the following loma code is illegal if y is not declared before:
        x : float
        y = x

        If we find an undeclared variable, raise an error.
    """

    class UndeclaredChecker(irvisitor.IRVisitor):
        ids = set()

        def visit_function_def(self, node):
            for arg in node.args:
                self.ids.add(arg.id)
            for stmt in node.body:
                self.visit_stmt(stmt)

        def visit_return(self, node):
            ret = self.visit_expr(node.val)
            if ret != None:
                raise error.UndeclaredVariable(ret, node)

        def visit_declare(self, node):
            if node.val != None:
                ret = self.visit_expr(node.val)
                if ret != None:
                    raise error.UndeclaredVariable(ret, node)
            self.ids.add(node.target)

        def visit_assign(self, node):
            ret = self.visit_expr(node.target)
            if ret != None:
                raise error.UndeclaredVariable(ret, node)
            ret = self.visit_expr(node.val)
            if ret != None:
                raise error.UndeclaredVariable(ret, node)

        def visit_ifelse(self, node):
            ret = self.visit_expr(node.cond)
            if ret != None:
                raise error.UndeclaredVariable(ret, node.cond)
            for stmt in node.then_stmts:
                self.visit_stmt(stmt)
            for stmt in node.else_stmts:
                self.visit_stmt(stmt)

        def visit_expr(self, node):
            match node:
                case loma_ir.Var():
                    return self.visit_var(node)
                case loma_ir.ArrayAccess():
                    return self.visit_array_access(node)
                case loma_ir.StructAccess():
                    return self.visit_struct_access(node)
                case loma_ir.ConstFloat():
                    return self.visit_const_float(node)
                case loma_ir.ConstInt():
                    return self.visit_const_int(node)
                case loma_ir.BinaryOp():
                    return self.visit_binary_op(node)
                case loma_ir.Call():
                    return self.visit_call(node)
                case _:
                    assert False, f'Visitor error: unhandled expression {node}'

        def visit_var(self, node):
            if node.id not in self.ids:
                return node.id
            else:
                return None

        def visit_while(self, node):
            ret = self.visit_expr(node.cond)
            if ret != None:
                raise error.UndeclaredVariable(ret, node.cond)
            for stmt in node.body:
                self.visit_stmt(stmt)

        def visit_array_access(self, node):
            ret = self.visit_expr(node.array)
            if ret != None:
                return ret
            return self.visit_expr(node.index)

        def visit_struct_access(self, node):
            return self.visit_expr(node.struct)

        def visit_binary_op(self, node):
            ret = self.visit_expr(node.left)
            if ret != None:
                return ret
            return self.visit_expr(node.right)

        def visit_call(self, node):
            for arg in node.args:
                ret = self.visit_expr(arg)
                if ret != None:
                    return ret
            return None

    UndeclaredChecker().visit_function(node)

def check_return_is_last(node : loma_ir.func):
    """ Check if the return statement is the last statement in the function,
        and is not in an if/while statement.
        For example, the following loma code is illegal:
        def f(x : In[int]) -> int:
            return 2 * x
            y : int = x
        The following loma code is also illegal:
        def f(x : In[int]) -> int:
            if x > 0:
                return 2 * x
    """

    class ReturnChecker(irvisitor.IRVisitor):
        def visit_function_def(self, node):
            for i, stmt in enumerate(node.body):
                self.is_last_statement = i == len(node.body) - 1
                self.visit_stmt(stmt)

        def visit_return(self, node):
            if not self.is_last_statement:
                raise error.ReturnNotLastStmt(node)

    ReturnChecker().visit_function(node)

def check_declare_bounded(node : loma_ir.func):
    """ Check if all variable declaration has bounded size.
        For example, the following loma code is illegal:
        def f():
            x : Array[float]
        The following loma code is also illegal
        class Foo:
            x : Array[float]
        def f():
            y : Foo
    """

    def is_bounded_size_type(t):
        match t:
            case loma_ir.Int():
                return True
            case loma_ir.Float():
                return True
            case loma_ir.Array():
                if t.static_size == None:
                    return False
                return is_bounded_size_type(t.t)
            case loma_ir.Struct():
                for m in t.members:
                    if not is_bounded_size_type(m.t):
                        return False
                return True
            case loma_ir.Diff():
                return is_bounded_size_type(t.t)

    class DeclareBoundChecker(irvisitor.IRVisitor):
        def visit_declare(self, node):
            if not is_bounded_size_type(node.t):
                raise error.DeclareUnboundedArray(node)

    DeclareBoundChecker().visit_function(node)

def check_unhandled_differentiation(node : loma_ir.func):
    """ Check if there are ForwardDiff or ReverseDiff
        functions that are not resolved into a FunctionDef
        (see autodiff.differentiate for more details).

        If we find such case, raise an error.
    """

    class UnhandledDiffChecker(irvisitor.IRVisitor):
        def visit_forward_diff(self, node):
            raise error.UnhandledDifferentiation(node.id, node.lineno)

        def visit_reverse_diff(self, node):
            raise error.UnhandledDifferentiation(node.id, node.lineno)

    UnhandledDiffChecker().visit_function(node)

def check_ir(structs : dict[str, loma_ir.Struct],
             diff_structs : dict[str, loma_ir.Struct],
             funcs : dict[str, loma_ir.func],
             check_diff : bool):
    """ Performs checks and type inferences on the loma functions (funcs).
        Fill in the type information of expressions.
        Raise errors when we see illegal code.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        diff_structs - a dictionary that maps the ID of the primal
                Struct to the corresponding differential Struct
                e.g., diff_structs['float'] returns _dfloat
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
        check_diff - whether we perform check_unhandled_differentiation
                     or not.
    """

    for f in funcs.values():
        if check_diff:
            check_unhandled_differentiation(f)
        check_duplicate_declare(f)
        check_undeclared_vars(f)
        check_return_is_last(f)
        check_declare_bounded(f)

    type_inference.check_and_infer_types(structs, diff_structs, funcs)
