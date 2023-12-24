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

def check_ir(node):
    check_duplicate_declare(node)
