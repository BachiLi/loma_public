import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import error
import visitor

# TODO: add scope
def check_duplicate_declare(node):
    class DuplicateChecker(visitor.IRVisitor):
        ids_lineno_map = {}

        def visit_function(self, node):
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

def check_undeclared_vars(node):
    class UndeclaredChecker(visitor.IRVisitor):
        ids = set()

        def visit_function(self, node):
            for arg in node.args:
                self.ids.add(arg.id)
            for stmt in node.body:
                self.visit_stmt(stmt)

        def visit_declare(self, node):
            self.ids.add(node.target)

        def visit_assign(self, node):
            ref = node.target
            if isinstance(ref, loma_ir.RefName):
                if ref.id not in self.ids:
                    raise error.UndeclaredVariable(ref.id, node.lineno)

    UndeclaredChecker().visit_function(node)

def check_ir(structs, funcs):
    for f in funcs.values():
        check_duplicate_declare(f)
        check_undeclared_vars(f)
