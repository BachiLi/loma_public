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
    body = [visit_stmt(b) for b in node.body]
    return loma_ir.Function(node.name, args, body, lineno = node.lineno)

def visit_stmt(node):
    if isinstance(node, ast.Return):
      return loma_ir.Return(visit_expr(node.value), lineno = node.lineno)
    elif isinstance(node, ast.AnnAssign):
      return loma_ir.Declare(node.target.id, visit_expr(node.value), lineno = node.lineno)
    elif isinstance(node, ast.Assign):
      assert len(node.targets) == 1
      return loma_ir.Assign(node.targets[0].id, visit_expr(node.value), lineno = node.lineno)
    else:
      assert False, f'Unknown statement {type(node).__name__}'

def visit_expr(node):
    if isinstance(node, ast.Name):
      return loma_ir.Var(node.id, lineno = node.lineno)
    elif isinstance(node, ast.Constant):
      return loma_ir.Const(float(node.value), lineno = node.lineno)
    elif isinstance(node, ast.BinOp):
      if isinstance(node.op, ast.Add):
        return loma_ir.Add(visit_expr(node.left), visit_expr(node.right), lineno = node.lineno)
      elif isinstance(node.op, ast.Sub):
        return loma_ir.Sub(visit_expr(node.left), visit_expr(node.right), lineno = node.lineno)
      elif isinstance(node.op, ast.Mult):
        return loma_ir.Mul(visit_expr(node.left), visit_expr(node.right), lineno = node.lineno)
      elif isinstance(node.op, ast.Div):
        return loma_ir.Div(visit_expr(node.left), visit_expr(node.right), lineno = node.lineno)
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
