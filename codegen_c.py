import attrs
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irvisitor
import compiler

def type_to_string(node : loma_ir.type | loma_ir.arg) -> str:
    """ Given a loma type, return a string that represents
        the type in C.
    """

    match node:
        case loma_ir.Arg():
            if isinstance(node.t, loma_ir.Array):
                return type_to_string(node.t)
            else:
                return type_to_string(node.t) + ('*' if node.i == loma_ir.Out() else '')
        case loma_ir.Int():
            return 'int'
        case loma_ir.Float():
            return 'float'
        case loma_ir.Array():
            return type_to_string(node.t) + '*'
        case loma_ir.Struct():
            return node.id
        case None:
            return 'void'
        case _:
            assert False

@attrs.define()
class CCodegenVisitor(irvisitor.IRVisitor):
    """ Generates C code from loma IR.
    """

    code = ''
    tab_count = 0
    funcs_defs = None

    def __init__(self, func_defs):
        self.func_defs = func_defs

    def emit_tabs(self):
        self.code += '\t' * self.tab_count

    def visit_function_def(self, node):
        self.code += f'{type_to_string(node.ret_type)} {node.id}('
        for i, arg in enumerate(node.args):
            if i > 0:
                self.code += ', '
            self.code += f'{type_to_string(arg)} {arg.id}'
        if node.is_simd:
            if len(node.args) > 0:
                self.code += ', '
            self.code += 'int __total_work'
        self.code += ') {\n'
        self.byref_args = set([arg.id for arg in node.args if \
            arg.i == loma_ir.Out() and (not isinstance(arg.t, loma_ir.Array))])

        self.tab_count += 1
        if node.is_simd:
            self.emit_tabs()
            self.code += 'for (int __work_id = 0; __work_id < __total_work; __work_id++) {\n'
            self.tab_count += 1
        for stmt in node.body:
            self.visit_stmt(stmt)
        if node.is_simd:
            self.tab_count -= 1
            self.emit_tabs()
            self.code += '}\n'
        self.tab_count -= 1
        self.code += '}\n'

    def visit_return(self, node):
        self.emit_tabs()
        self.code += f'return {self.visit_expr(node.val)};\n'

    def init_zero(self, id, t, depth = 0):
        # Initiailize the declared variable to zero
        if isinstance(t, loma_ir.Int) or isinstance(t, loma_ir.Float):
            self.emit_tabs()
            self.code += f'{id} = 0;\n'
        elif isinstance(t, loma_ir.Struct):
            for m in t.members:
                self.init_zero(id + '.' + m.id, m.t, depth)
        elif isinstance(t, loma_ir.Array):
            self.emit_tabs()
            iter_var_name = 'i'
            self.code += f'for (int _{iter_var_name * (depth + 1)} = 0;' + \
                         f' _{iter_var_name * (depth + 1)} < {t.static_size};' + \
                         f'_{iter_var_name * (depth + 1)}++) {{\n'

            self.tab_count += 1
            self.init_zero(id + f'[_{iter_var_name * (depth + 1)}]', t.t, depth + 1)
            self.tab_count -= 1
            
            self.emit_tabs()
            self.code += '}\n'

    def visit_declare(self, node):
        self.emit_tabs()
        if not isinstance(node.t, loma_ir.Array):
            self.code += f'{type_to_string(node.t)} {node.target}'
        else:
            # Special rule for arrays
            assert node.t.static_size != None
            self.code += f'{type_to_string(node.t.t)} {node.target}[{node.t.static_size}]'
        if node.val is not None:
            self.code += f' = {self.visit_expr(node.val)};\n'
        else:
            self.code += ';\n'
            self.init_zero(node.target, node.t)

    def visit_assign(self, node):
        self.emit_tabs()
        self.code += self.visit_expr(node.target)
        expr_str = self.visit_expr(node.val)
        if expr_str != '':
            self.code += f' = {expr_str}'
        self.code += ';\n'

    def visit_ifelse(self, node):
        self.emit_tabs()
        self.code += f'if ({self.visit_expr(node.cond)}) {{\n'
        self.tab_count += 1
        for stmt in node.then_stmts:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        self.emit_tabs()
        self.code += f'}} else {{\n'
        self.tab_count += 1
        for stmt in node.else_stmts:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        self.emit_tabs()
        self.code += '}\n'

    def visit_while(self, node):
        self.emit_tabs()
        self.code += f'while ({self.visit_expr(node.cond)}) {{\n'
        self.tab_count += 1
        for stmt in node.body:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        self.emit_tabs()
        self.code += '}\n'

    def visit_call_stmt(self, node):
        self.emit_tabs()
        self.code += self.visit_expr(node.call) + ';\n'

    def visit_expr(self, node):
        match node:
            case loma_ir.Var():
                if node.id in self.byref_args:
                    return '(*' + node.id + ')'
                else:
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
                if node.id == 'thread_id':
                    return '__work_id'
                elif node.id == 'atomic_add':
                    arg0_str = self.visit_expr(node.args[0])
                    arg1_str = self.visit_expr(node.args[1])
                    return f'{arg0_str} += {arg1_str}'
                func_id = node.id
                # call the single precision versions of the intrinsic functions
                if func_id == 'sin':
                    func_id = 'sinf'
                elif func_id == 'cos':
                    func_id = 'cosf'
                elif func_id == 'sqrt':
                    func_id = 'sqrtf'
                elif func_id == 'pow':
                    func_id = 'powf'
                elif func_id == 'exp':
                    func_id = 'expf'
                elif func_id == 'log':
                    func_id = 'logf'
                elif func_id == 'int2float':
                    func_id = '(float)'
                elif func_id == 'float2int':
                    func_id = '(int)'

                ret = f'{func_id}('
                if func_id in self.func_defs:
                    func_def = self.func_defs[func_id]
                    arg_strs = [self.visit_expr(arg) for arg in node.args]
                    for i, arg in enumerate(arg_strs):
                        if func_def.args[i].i == loma_ir.Out() and \
                                (not isinstance(func_def.args[i].t, loma_ir.Array)):
                            arg_strs[i] = '&(' + arg + ')'
                    ret += ','.join(arg_strs)
                else:
                    ret += ','.join([self.visit_expr(arg) for arg in node.args])
                ret += ')'
                return ret
            case None:
                return ''
            case _:
                assert False, f'Visitor error: unhandled expression {expr}'

def codegen_c(structs : dict[str, loma_ir.Struct],
              funcs : dict[str, loma_ir.func]) -> str:
    """ Given loma Structs (structs) and loma functions (funcs),
        return a string that represents the equivalent C code.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
    """

    sorted_structs_list = compiler.topo_sort_structs(structs)

    # Definition of structs
    code = ''
    for s in sorted_structs_list:
        code += f'typedef struct {{\n'
        for m in s.members:
            # Special rule for arrays
            if isinstance(m.t, loma_ir.Array) and m.t.static_size is not None:
                code += f'\t{type_to_string(m.t.t)} {m.id}[{m.t.static_size}];\n'
            else:
                code += f'\t{type_to_string(m.t)} {m.id};\n'
        code += f'}} {s.id};\n'

    # Forward declaration of functions
    for f in funcs.values():
        code += f'{type_to_string(f.ret_type)} {f.id}('
        for i, arg in enumerate(f.args):
            if i > 0:
                code += ', '
            code += f'{type_to_string(arg)} {arg.id}'
        if f.is_simd:
            if len(f.args) > 0:
                code += ', '
            code += 'int __total_work'
        code += ');\n'

    for f in funcs.values():
        cg = CCodegenVisitor(funcs)
        cg.visit_function(f)
        code += cg.code
    return code
