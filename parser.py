import inspect
import ast
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def annotation_to_type(node):
    if type(node) == ast.Name:
        if node.id == 'int':
            return loma_ir.Int()
        elif node.id == 'float':
            return loma_ir.Float()
        else:
            # TODO: error message
            assert False
    elif type(node) == ast.Subscript:
        assert type(node.value) == ast.Name
        if node.value.id == 'In' or node.value.id == 'Out':
            # Ignore input/output qualifiers
            return annotation_to_type(node.slice)
        assert node.value.id == 'Array'
        return loma_ir.Array(annotation_to_type(node.slice))
    else:
        assert False

def annotation_to_inout(node):
    assert type(node) == ast.Subscript
    assert type(node.value) == ast.Name
    if node.value.id == 'In':
        return loma_ir.In()
    elif node.value.id == 'Out':
        return loma_ir.Out()
    else:
        assert False

def ast_cmp_op_convert(node):
    if isinstance(node, ast.Lt):
        return loma_ir.Less()
    elif isinstance(node, ast.LtE):
        return loma_ir.LessEqual()
    elif isinstance(node, ast.Gt):
        return loma_ir.Greater()
    elif isinstance(node, ast.GtE):
        return loma_ir.GreaterEqual()
    elif isinstance(node, ast.Eq):
        return loma_ir.Equal()
    elif isinstance(node, ast.And):
        return loma_ir.And()
    elif isinstance(node, ast.Or):
        return loma_ir.Or()
    else:
        assert False

def visit_FunctionDef(node):
    node_args = node.args
    assert node_args.vararg is None
    assert node_args.kwarg is None
    args = [loma_ir.Arg(arg.arg,
                        annotation_to_type(arg.annotation),
                        annotation_to_inout(arg.annotation)) for arg in node_args.args]
    body = [visit_stmt(b) for b in node.body]
    ret_type = None
    if node.returns:
        ret_type = annotation_to_type(node.returns)

    return loma_ir.Function(node.name,
                            args,
                            body,
                            ret_type = ret_type,
                            lineno = node.lineno)

def visit_stmt(node):
    if isinstance(node, ast.Return):
        return loma_ir.Return(visit_expr(node.value), lineno = node.lineno)
    elif isinstance(node, ast.AnnAssign):
        assert(type(node.annotation) == ast.Name)
        if node.annotation.id == 'int':
            t = loma_ir.Int()
        elif node.annotation.id == 'float':
            t = loma_ir.Float()
        else:
            # TODO: error message
            assert False
        return loma_ir.Declare(node.target.id,
                               t,
                               visit_expr(node.value),
                               lineno = node.lineno)
    elif isinstance(node, ast.Assign):
        assert len(node.targets) == 1
        target = node.targets[0]
        if type(target) == ast.Name:
            return loma_ir.Assign(target.id,
                                  visit_expr(node.value),
                                  lineno = node.lineno)
        elif type(target) == ast.Subscript:
            assert type(target.value) == ast.Name
            return loma_ir.Assign(target.value.id,
                                  visit_expr(node.value),
                                  index = visit_expr(target.slice),
                                  lineno = node.lineno)
    elif isinstance(node, ast.If):
        cond = visit_expr(node.test)
        then_stmts = [visit_stmt(s) for s in node.body]
        else_stmts = [visit_stmt(s) for s in node.orelse]
        return loma_ir.IfElse(cond, then_stmts, else_stmts)
    else:
        assert False, f'Unknown statement {type(node).__name__}'

def visit_expr(node):
    if isinstance(node, ast.Name):
      return loma_ir.Var(node.id, lineno = node.lineno)
    elif isinstance(node, ast.Constant):
      if type(node.value) == int:
          return loma_ir.ConstInt(node.value, lineno = node.lineno)  
      elif type(node.value) == float:
          return loma_ir.ConstFloat(node.value, lineno = node.lineno)
      else:
          assert False, f'Unknown constant type.'
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            return loma_ir.Sub(loma_ir.ConstInt(0), visit_expr(node.operand))
        else:
            assert False, f'Unknown UnaryOp {type(node.op).__name__}'
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
    elif isinstance(node, ast.Subscript):
        assert type(node.value) == ast.Name
        index = visit_expr(node.slice)
        return loma_ir.ArrayAccess(node.value.id, index)
    elif isinstance(node, ast.Compare):
        # print(node.__dict__)
        assert len(node.ops) == 1
        assert len(node.comparators) == 1
        op = ast_cmp_op_convert(node.ops[0])
        left = visit_expr(node.left)
        right = visit_expr(node.comparators[0])
        return loma_ir.Compare(op, left, right)
    elif isinstance(node, ast.BoolOp):
        op = ast_cmp_op_convert(node.op)
        assert len(node.values) == 2
        left = visit_expr(node.values[0])
        right = visit_expr(node.values[1])
        return loma_ir.Compare(op, left, right)
    else:
        assert False, f'Unknown expr {type(node).__name__}'

def parse(func):
    code = inspect.getsource(func)
    module = ast.parse(code)

    # Assume we only have one function definition.
    assert(len(module.body) == 1)
    assert(type(module.body[0]) == ast.FunctionDef)
    return visit_FunctionDef(module.body[0])
