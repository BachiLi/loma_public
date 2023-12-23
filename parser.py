import inspect
import ast
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def visit_FunctionDef(node):
    args = node.args
    assert(args.vararg is None)
    assert(args.kwarg is None)
    args = [arg.arg for arg in args.args]
    body = loma_ir.Block([visit_stmt(b) for b in node.body])
    return loma_ir.Function(node.name, args, body)

def visit_stmt(node):
    if isinstance(node, ast.Return):
      return loma_ir.Return(visit_expr(node.value))
    else:
      assert False, f'Unknown statement {type(node).__name__}'

def visit_expr(node):
    if isinstance(node, ast.Name):
      return loma_ir.Var(node.id)
    elif isinstance(node, ast.BinOp):
      if isinstance(node.op, ast.Add):
        return loma_ir.Add(visit_expr(node.left), visit_expr(node.right))
      else:
        assert False, f'Unknown BinOp {type(node.op).__name__}'
    else:
      assert False, f'Unknown expr {type(node).__name__}'

def parse(func):
    code = inspect.getsource(func)
    module = ast.parse(code)

    # Assume we only have one function definition.
    assert(len(module.body) == 1)
    assert(type(module.body[0]) == ast.FunctionDef)
    return visit_FunctionDef(module.body[0])
