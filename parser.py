import inspect
import ast
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def annotation_to_type(node):
    match node:
        case ast.Name():
            if node.id == 'int':
                return loma_ir.Int()
            elif node.id == 'float':
                return loma_ir.Float()
            else:
                # Struct members to be filled later
                return loma_ir.Struct(node.id, [])
        case ast.Subscript():
            assert isinstance(node.value, ast.Name)
            if node.value.id == 'In' or node.value.id == 'Out':
                # Ignore input/output qualifiers
                return annotation_to_type(node.slice)
            assert node.value.id == 'Array'
            array_type = node.slice
            static_size = None
            if isinstance(array_type, ast.Tuple):
                assert len(array_type.elts) == 2 # TODO: error message
                assert isinstance(array_type.elts[1], ast.Constant)
                static_size = int(array_type.elts[1].value)
                array_type = array_type.elts[0]
            return loma_ir.Array(annotation_to_type(array_type), static_size)
        case _:
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
    match node:
        case ast.Lt():
            return loma_ir.Less()
        case ast.LtE():
            return loma_ir.LessEqual()
        case ast.Gt():
            return loma_ir.Greater()
        case ast.GtE():
            return loma_ir.GreaterEqual()
        case ast.Eq():
            return loma_ir.Equal()
        case ast.And():
            return loma_ir.And()
        case ast.Or():
            return loma_ir.Or()
        case _:
            assert False

def parse_ref(node):
    match node:
        case ast.Name():
            return loma_ir.RefName(node.id)
        case ast.Subscript():
            return loma_ir.RefArray(parse_ref(node.value),
                                    visit_expr(node.slice))
        case ast.Attribute():
            return loma_ir.RefStruct(parse_ref(node.value),
                                     node.attr)
        case _:
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

    is_simd = False
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            if decorator.id == 'simd':
                is_simd = True

    return loma_ir.FunctionDef(node.name,
                               args,
                               body,
                               is_simd,
                               ret_type = ret_type,
                               lineno = node.lineno)

def visit_ClassDef(node):
    members = []
    for member in node.body:
        match member:
            case ast.AnnAssign():
                assert isinstance(member.target, ast.Name)
                t = annotation_to_type(member.annotation)
                members.append(loma_ir.MemberDef(member.target.id, t))
            case _:
                assert False, f'Unknown class member statement {type(member).__name__}'
    return loma_ir.Struct(node.name, members, lineno = node.lineno)

def visit_stmt(node):
    match node:
        case ast.Return():
            return loma_ir.Return(visit_expr(node.value), lineno = node.lineno)
        case ast.AnnAssign():
            t = annotation_to_type(node.annotation)
            return loma_ir.Declare(node.target.id,
                                   t,
                                   visit_expr(node.value),
                                   lineno = node.lineno)
        case ast.Assign():
            assert len(node.targets) == 1
            target = node.targets[0]
            return loma_ir.Assign(parse_ref(target),
                                  visit_expr(node.value),
                                  lineno = node.lineno)
        case ast.If():
            cond = visit_expr(node.test)
            then_stmts = [visit_stmt(s) for s in node.body]
            else_stmts = [visit_stmt(s) for s in node.orelse]
            return loma_ir.IfElse(cond,
                                  then_stmts,
                                  else_stmts,
                                  lineno = node.lineno)
        case ast.While():
            cond = visit_expr(node.test)
            body = [visit_stmt(s) for s in node.body]
            return loma_ir.While(cond, body, lineno = node.lineno)
        case _:
            assert False, f'Unknown statement {type(node).__name__}'

def visit_expr(node):
    match node:
        case ast.Name():
            return loma_ir.Var(node.id, lineno = node.lineno)
        case ast.Constant():
            if type(node.value) == int:
                return loma_ir.ConstInt(node.value, lineno = node.lineno)  
            elif type(node.value) == float:
                return loma_ir.ConstFloat(node.value, lineno = node.lineno)
            else:
                assert False, f'Unknown constant type'
        case ast.UnaryOp():
            if isinstance(node.op, ast.USub):
                return loma_ir.BinaryOp(loma_ir.Sub(), loma_ir.ConstInt(0), visit_expr(node.operand))
            else:
                assert False, f'Unknown UnaryOp {type(node.op).__name__}'
        case ast.BinOp():
            match node.op:
                case ast.Add():
                    return loma_ir.BinaryOp(loma_ir.Add(),
                                            visit_expr(node.left),
                                            visit_expr(node.right),
                                            lineno = node.lineno)
                case ast.Sub():
                    return loma_ir.BinaryOp(loma_ir.Sub(),
                                            visit_expr(node.left),
                                            visit_expr(node.right),
                                            lineno = node.lineno)
                case ast.Mult():
                    return loma_ir.BinaryOp(loma_ir.Mul(),
                                            visit_expr(node.left),
                                            visit_expr(node.right),
                                            lineno = node.lineno)
                case ast.Div():
                    return loma_ir.BinaryOp(loma_ir.Div(),
                                            visit_expr(node.left),
                                            visit_expr(node.right),
                                            lineno = node.lineno)
                case _:
                    assert False, f'Unknown BinOp {type(node.op).__name__}'
        case ast.Subscript():
            return loma_ir.ArrayAccess(parse_ref(node.value), visit_expr(node.slice))
        case ast.Attribute():
            return loma_ir.StructAccess(parse_ref(node.value), node.attr)
        case ast.Compare():
            assert len(node.ops) == 1
            assert len(node.comparators) == 1
            op = ast_cmp_op_convert(node.ops[0])
            left = visit_expr(node.left)
            right = visit_expr(node.comparators[0])
            return loma_ir.BinaryOp(op, left, right)
        case ast.BoolOp():
            op = ast_cmp_op_convert(node.op)
            assert len(node.values) == 2
            left = visit_expr(node.values[0])
            right = visit_expr(node.values[1])
            return loma_ir.BinaryOp(op, left, right)
        case ast.Call():
            assert type(node.func) == ast.Name
            return loma_ir.Call(node.func.id, [visit_expr(arg) for arg in node.args])
        case None:
            return None
        case _:
            assert False, f'Unknown expr {type(node).__name__}'

def parse(code):
    module = ast.parse(code)
    structs = {}
    for d in module.body:
        if isinstance(d, ast.ClassDef):
            s = visit_ClassDef(d)
            structs[s.id] = s

    funcs = {}
    for d in module.body:
        if isinstance(d, ast.FunctionDef):
            f = visit_FunctionDef(d)
            funcs[f.id] = f

    return structs, funcs
