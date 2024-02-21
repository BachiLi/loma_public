import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import error
import irvisitor
import type_inference

# TODO: add scope
def check_duplicate_declare(node : loma_ir.func):
    """ Check if there are duplicated declaration of variables in loma code.
        For example, the following loma code is illegal:
        x : float
        x : int

        If we find a duplicated declaration, raise an error.
    """

    class DuplicateChecker(irvisitor.IRVisitor):
        ids_lineno_map = {}

        def visit_function_def(self, node):
            for arg in node.args:
                self.ids_lineno_map[arg.id] = node.lineno
            for stmt in node.body:
                self.visit_stmt(stmt)

        def visit_declare(self, node):
            if node.target in self.ids_lineno_map:
                raise error.DuplicateVariable(node.target,
                                              self.ids_lineno_map[node.target],
                                              node.lineno)
            self.ids_lineno_map[node.target] = node.lineno

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

        def visit_declare(self, node):
            self.ids.add(node.target)

        def visit_assign(self, node):
            ref = node.target
            if isinstance(ref, loma_ir.Var):
                if ref.id not in self.ids:
                    raise error.UndeclaredVariable(ref.id, node.lineno)

    UndeclaredChecker().visit_function(node)

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

    type_inference.check_and_infer_types(structs, diff_structs, funcs)
