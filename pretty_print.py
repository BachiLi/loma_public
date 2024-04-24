import attrs
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irvisitor
import compiler

def type_to_string(node : loma_ir.type) -> str:
    """ Given a loma type, return a string that represents
        the type.
    """

    match node:
        case loma_ir.Int():
            return 'int'
        case loma_ir.Float():
            return 'float'
        case loma_ir.Array():
            if node.static_size != None:
                return f'Array[{type_to_string(node.t)}, {node.static_size}]'
            else:
                return f'Array[{type_to_string(node.t)}]'
        case loma_ir.Struct():
            return node.id
        case loma_ir.Diff():
            return f'Diff[{type_to_string(node.t)}]'
        case None:
            return 'void'
        case _:
            assert False

def arg_to_string(arg : loma_ir.arg) -> str:
    if arg.i == loma_ir.In():
        return f'{arg.id} : In[{type_to_string(arg.t)}]'
    else:
        return f'{arg.id} : Out[{type_to_string(arg.t)}]'

@attrs.define()
class PrettyPrintVisitor(irvisitor.IRVisitor):
    """ Generates pseudo code from loma IR.
    """

    code = ''
    tab_count = 0

    def emit_tabs(self):
        self.code += '\t' * self.tab_count

    def visit_function_def(self, node):
        if node.is_simd:
            self.code += '@simd\n'
        self.code += f'def {node.id}('
        for i, arg in enumerate(node.args):
            if i > 0:
                self.code += ', '
            self.code += arg_to_string(arg)
        self.code += f') -> {type_to_string(node.ret_type)}:\n'
        self.tab_count += 1
        for stmt in node.body:
            self.visit_stmt(stmt)
        self.tab_count -= 1

    def visit_forward_diff(self, node):
        self.code += f'{node.id} = fwd_diff({node.primal_func})'

    def visit_reverse_diff(self, node):
        self.code += f'{node.id} = rev_diff({node.primal_func})'

    def visit_return(self, node):
        self.emit_tabs()
        self.code += f'return {self.visit_expr(node.val)}\n'

    def visit_declare(self, node):
        self.emit_tabs()
        self.code += f'{node.target} : {type_to_string(node.t)}'
        if node.val is not None:
            self.code += f' = {self.visit_expr(node.val)}'
        self.code += '\n'

    def visit_assign(self, node):
        self.emit_tabs()
        self.code += self.visit_expr(node.target)
        expr_str = self.visit_expr(node.val)
        if expr_str != '':
            self.code += f' = {expr_str}'
        self.code += '\n'

    def visit_ifelse(self, node):
        self.emit_tabs()
        self.code += f'if {self.visit_expr(node.cond)}:\n'
        self.tab_count += 1
        for stmt in node.then_stmts:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        if len(node.else_stmts) > 0:
            self.emit_tabs()
            self.code += f'else:\n'
            self.tab_count += 1
            for stmt in node.else_stmts:
                self.visit_stmt(stmt)
            self.tab_count -= 1

    def visit_call_stmt(self, node):
        self.emit_tabs()
        self.code += self.visit_expr(node.call) + '\n'

    def visit_while(self, node):
        self.emit_tabs()
        self.code += f'while {self.visit_expr(node.cond)} :\n'
        self.tab_count += 1
        for stmt in node.body:
            self.visit_stmt(stmt)
        self.tab_count -= 1

    def visit_expr(self, node):
        match node:
            case loma_ir.Var():
                return node.id
            case loma_ir.ArrayAccess():
                return f'({self.visit_expr(node.array)})[{self.visit_expr(node.index)}]'
            case loma_ir.StructAccess():
                return f'({self.visit_expr(node.struct)}).{node.member_id}'
            case loma_ir.ConstFloat():
                return f'(float)({node.val})'
            case loma_ir.ConstInt():
                return f'(int)({node.val})'
            case loma_ir.BinaryOp():
                match node.op:
                    case loma_ir.Add():
                        return f'({self.visit_expr(node.left)}) + ({self.visit_expr(node.right)})'
                    case loma_ir.Sub():
                        return f'({self.visit_expr(node.left)}) - ({self.visit_expr(node.right)})'
                    case loma_ir.Mul():
                        return f'({self.visit_expr(node.left)}) * ({self.visit_expr(node.right)})'
                    case loma_ir.Div():
                        return f'({self.visit_expr(node.left)}) / ({self.visit_expr(node.right)})'
                    case loma_ir.Less():
                        return f'({self.visit_expr(node.left)}) < ({self.visit_expr(node.right)})'
                    case loma_ir.LessEqual():
                        return f'({self.visit_expr(node.left)}) <= ({self.visit_expr(node.right)})'
                    case loma_ir.Greater():
                        return f'({self.visit_expr(node.left)}) > ({self.visit_expr(node.right)})'
                    case loma_ir.GreaterEqual():
                        return f'({self.visit_expr(node.left)}) >= ({self.visit_expr(node.right)})'
                    case loma_ir.Equal():
                        return f'({self.visit_expr(node.left)}) == ({self.visit_expr(node.right)})'
                    case loma_ir.And():
                        return f'({self.visit_expr(node.left)}) && ({self.visit_expr(node.right)})'
                    case loma_ir.Or():
                        return f'({self.visit_expr(node.left)}) || ({self.visit_expr(node.right)})'
                    case _:
                        assert False
            case loma_ir.Call():
                func_id = node.id
                ret = f'{func_id}('
                ret += ','.join([self.visit_expr(arg) for arg in node.args])
                ret += ')'
                return ret
            case None:
                return ''
            case _:
                assert False, f'Visitor error: unhandled expression {expr}'

def struct_to_str(s : loma_ir.Struct) -> str:
    code = f'class {s.id}:\n'
    for m in s.members:
        # Special rule for arrays
        code += f'\t{m.id} : {type_to_string(m.t)}'
    return code

def func_to_str(f : loma_ir.func) -> str:
    ppv = PrettyPrintVisitor()
    ppv.visit_function(f)
    return ppv.code

def stmt_to_str(s : loma_ir.stmt) -> str:
    ppv = PrettyPrintVisitor()
    ppv.visit_stmt(s)
    return ppv.code

def expr_to_str(e : loma_ir.expr) -> str:
    ppv = PrettyPrintVisitor()
    ppv.visit_expr(e)
    return ppv.code

def loma_to_str(node) -> str:
    match node:
        case loma_ir.func():
            return func_to_str(node)
        case loma_ir.stmt():
            return stmt_to_str(node)
        case loma_ir.expr():
            return expr_to_str(node)
        case loma_ir.arg():
            return arg_to_str(node)
        case _:
            assert False

def pretty_print_stmts(stmts : list[loma_ir.stmt]):
    code = ''
    for s in stmts:
        code += stmt_to_str(s)

    print(code)

def pretty_print(structs : dict[str, loma_ir.Struct],
                 funcs : dict[str, loma_ir.func]):
    """ Given loma Structs (structs) and loma functions (funcs),
        print out pseudo code that represents the IR.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
    """
    # Definition of structs
    code = ''
    for s in structs.values():
        code += struct_to_str(s)
        code += '\n'

    for f in funcs.values():
        code += func_to_str(f)
        code += '\n'

    print(code)
