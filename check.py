import _asdl.loma as loma_ir
import error
import visitor

# TODO: add scope
def check_duplicate_declare(node):
    class DuplicateChecker(visitor.IRVisitor):
        ids_lineno_map = {}

        def visit_declare(self, node):
            if node.target in self.ids_lineno_map:
                raise error.DuplicateVariable(node.target,
                                              self.ids_lineno_map[node.target],
                                              node.lineno)
            self.ids_lineno_map[node.target] = node.lineno

    DuplicateChecker().visit_function(node)

def check_undeclared_vars(node):
    class UndeclaredChecker(visitor.IRVisitor):
        ids = set()

        def visit_declare(self, node):
            self.ids.add(node.target)

        def visit_assign(self, node):
            if node.target not in self.ids:
                raise error.UndeclaredVariable(node.target, node.lineno)

    UndeclaredChecker().visit_function(node)

def check_ir(node):
    check_duplicate_declare(node)
    check_undeclared_vars(node)
