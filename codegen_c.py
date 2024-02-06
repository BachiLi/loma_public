import attrs
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import irvisitor

def type_to_string(node):
    match node:
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
    code = ''
    tab_count = 0

    def emit_tabs(self):
        self.code += '\t' * self.tab_count

    def visit_function_def(self, node):
        self.code += f'extern \"C\" {type_to_string(node.ret_type)} {node.id}('
        for i, arg in enumerate(node.args):
            if i > 0:
                self.code += ', '
            self.code += f'{type_to_string(arg.t)} {arg.id}'
        if node.is_simd:
            if len(node.args) > 0:
                self.code += ', '
            self.code += 'int __total_work'
        self.code += ') {\n'
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

    def visit_return(self, ret):
        self.emit_tabs()
        self.code += f'return {self.visit_expr(ret.val)};\n'

    def visit_declare(self, dec):
        self.emit_tabs()
        if not isinstance(dec.t, loma_ir.Array):
            self.code += f'{type_to_string(dec.t)} {dec.target}'
        else:
            # Special rule for arrays
            assert dec.t.static_size != None
            self.code += f'{type_to_string(dec.t.t)} {dec.target}[{dec.t.static_size}]'
        expr_str = self.visit_expr(dec.val)
        if expr_str != '':
            self.code += f' = {expr_str}'
        self.code += ';\n'

    def visit_assign(self, ass):
        self.emit_tabs()
        self.code += self.visit_ref(ass.target)
        expr_str = self.visit_expr(ass.val)
        if expr_str != '':
            self.code += f' = {expr_str}'
        self.code += ';\n'

    def visit_ifelse(self, ifelse):
        self.emit_tabs()
        self.code += f'if ({self.visit_expr(ifelse.cond)}) {{\n'
        self.tab_count += 1
        for stmt in ifelse.then_stmts:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        self.emit_tabs()
        self.code += f'}} else {{\n'
        self.tab_count += 1
        for stmt in ifelse.else_stmts:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        self.emit_tabs()
        self.code += '}\n'

    def visit_while(self, loop):
        self.emit_tabs()
        self.code += f'while ({self.visit_expr(loop.cond)}) {{\n'
        self.tab_count += 1
        for stmt in loop.body:
            self.visit_stmt(stmt)
        self.tab_count -= 1
        self.emit_tabs()
        self.code += '}\n'

    def visit_expr(self, expr):
        match expr:
            case loma_ir.Var():
                return expr.id
            case loma_ir.ArrayAccess():
                return f'({self.visit_expr(expr.array)})[{self.visit_expr(expr.index)}]'
            case loma_ir.StructAccess():
                return f'({self.visit_expr(expr.struct)}).{expr.member_id}'
            case loma_ir.ConstFloat():
                return f'(float)({expr.val})'
            case loma_ir.ConstInt():
                return f'(int)({expr.val})'
            case loma_ir.BinaryOp():
                match expr.op:
                    case loma_ir.Add():
                        return f'({self.visit_expr(expr.left)}) + ({self.visit_expr(expr.right)})'
                    case loma_ir.Sub():
                        return f'({self.visit_expr(expr.left)}) - ({self.visit_expr(expr.right)})'
                    case loma_ir.Mul():
                        return f'({self.visit_expr(expr.left)}) * ({self.visit_expr(expr.right)})'
                    case loma_ir.Div():
                        return f'({self.visit_expr(expr.left)}) / ({self.visit_expr(expr.right)})'
                    case loma_ir.Less():
                        return f'({self.visit_expr(expr.left)}) < ({self.visit_expr(expr.right)})'
                    case loma_ir.LessEqual():
                        return f'({self.visit_expr(expr.left)}) <= ({self.visit_expr(expr.right)})'
                    case loma_ir.Greater():
                        return f'({self.visit_expr(expr.left)}) > ({self.visit_expr(expr.right)})'
                    case loma_ir.GreaterEqual():
                        return f'({self.visit_expr(expr.left)}) >= ({self.visit_expr(expr.right)})'
                    case loma_ir.Equal():
                        return f'({self.visit_expr(expr.left)}) == ({self.visit_expr(expr.right)})'
                    case loma_ir.And():
                        return f'({self.visit_expr(expr.left)}) && ({self.visit_expr(expr.right)})'
                    case loma_ir.Or():
                        return f'({self.visit_expr(expr.left)}) || ({self.visit_expr(expr.right)})'
                    case _:
                        assert False
            case loma_ir.Call():
                if expr.id == 'thread_id':
                    return '__work_id'
                func_id = expr.id
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
                ret += ','.join([self.visit_expr(arg) for arg in expr.args])
                ret += ')'
                return ret
            case None:
                return ''
            case _:
                assert False, f'Visitor error: unhandled expression {expr}'

    def visit_ref(self, ref):
        match ref:
            case loma_ir.RefName():
                return ref.id
            case loma_ir.RefArray():
                return self.visit_ref(ref.array) + f'[{self.visit_expr(ref.index)}]'
            case loma_ir.RefStruct():
                return self.visit_ref(ref.struct) + f'.{ref.member}'
            case _:
                assert False, f'Visitor error: unhandled ref {ref}'


def codegen_c(structs, funcs):
    # Sort the struct topologically
    sorted_structs_list = []
    traversed_struct = set()
    def traverse_structs(s):
        if s in traversed_struct:
            return
        for m in s.members:
            if isinstance(m.t, loma_ir.Struct) or isinstance(m.t, loma_ir.Array):
                next_s = m.t if isinstance(m.t, loma_ir.Struct) else m.t.t
                if isinstance(next_s, loma_ir.Struct):
                    traverse_structs(structs[next_s.id])
        sorted_structs_list.append(s)
        traversed_struct.add(s)
    for s in structs.values():
        traverse_structs(s)

    # Definition of structs
    code = ''
    for s in sorted_structs_list:
        code += f'struct {s.id} {{\n'
        for m in s.members:
            code += f'\t{type_to_string(m.t)} {m.id};\n'
        code += f'}};\n'

    # Forward declaration of functions
    for f in funcs.values():
        code += f'extern \"C\" {type_to_string(f.ret_type)} {f.id}('
        for i, arg in enumerate(f.args):
            if i > 0:
                code += ', '
            code += f'{type_to_string(arg.t)} {arg.id}'
        if f.is_simd:
            if len(f.args) > 0:
                code += ', '
            code += 'int __work_id'
        code += ');\n'
    
    for f in funcs.values():
        cg = CCodegenVisitor()
        cg.visit_function(f)
        code += cg.code
    return code
