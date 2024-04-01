import ast
import attrs
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import pretty_print

class CompileError(Exception):
    pass

class UserError(CompileError):
    pass

@attrs.define(frozen=True)
class FuncArgNotAnnotated(UserError):
    node : ast.AST # Python AST Node

    def to_string(self):
        return (f'Function argument not annotated as In/Out.\n'
                f'Line {self.node.lineno}: {ast.unparse(self.node)}')

@attrs.define(frozen=True)
class DuplicateVariable(UserError):
    # the name of the variable that is duplicated
    var : str
    # the first declare statement (or arg)
    first_declare_stmt : loma_ir.stmt | loma_ir.arg
    # the duplicate statement (or arg)
    duplicate_declare_stmt : loma_ir.stmt | loma_ir.arg

    def to_string(self):
        return (f'Duplicated variable declaration detected.\n'
                f'Variable name: {self.var}.\n'
                f'First declared (line {self.first_declare_stmt.lineno}): {pretty_print.loma_to_str(self.first_declare_stmt)}'
                f'Duplicated declared (line {self.duplicate_declare_stmt.lineno}): {pretty_print.loma_to_str(self.duplicate_declare_stmt)}')

@attrs.define(frozen=True)
class UndeclaredVariable(UserError):
    # the name of the variable that is undeclared
    var : str
    # the statement or expr which this occurs
    stmt : loma_ir.stmt | loma_ir.expr

    def to_string(self):
        return (f'Undeclared variable use detected.\n'
                f'Variable name: {self.var}.\n'
                f'Statement/Expr (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class ReturnNotLastStmt(UserError):
    # the return statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'Return is not the last statement, or is inside an if/while statement.\n'
                f'Statement (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class DeclareUnboundedArray(UserError):
    # the declare statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'Variable declaration with unbounded size detected.\n'
                f'Statement (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class DeclarationNotOutmostLevel(UserError):
    # the declare statement 
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'Variable declarations must be at outmost level of a function.\n'
                f'Statement (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class CallWithOutArgNotInCallStmt(UserError):
    # the call expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Function calls with output arguments must be inside CallStmt.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')


@attrs.define(frozen=True)
class ArrayAccessTypeMismatch(UserError):
    # the access expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Detected an expression that index from a variable that is not an array.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')

@attrs.define(frozen=True)
class StructAccessTypeMismatch(UserError):
    # the access expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Detected an expression that access members from a variable that is not a struct.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')

@attrs.define(frozen=True)
class StructMemberNotFound(UserError):
    # the access expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'The struct member does not exist in the struct access expression.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')


@attrs.define(frozen=True)
class BinaryOpTypeMismatch(UserError):
    # the access expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Invalid BinaryOp expression.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')

@attrs.define(frozen=True)
class CallTypeMismatch(UserError):
    # the call expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Invalid Call arguments.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')

@attrs.define(frozen=True)
class ReturnTypeMismatch(UserError):
    # the return statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'Invalid Return type.\n'
                f'Stmt (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class AssignTypeMismatch(UserError):
    # the assign statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'Invalid Assign type.\n'
                f'Stmt (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')    

@attrs.define(frozen=True)
class DeclareTypeMismatch(UserError):
    # the assign statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'Invalid Declare type.\n'
                f'Stmt (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')   

@attrs.define(frozen=True)
class IfElseCondTypeMismatch(UserError):
    # the ifelse cond expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Invalid IfElse condition.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')

@attrs.define(frozen=True)
class CallIDNotFound(UserError):
    # the call expr
    expr : loma_ir.expr

    def to_string(self):
        return (f'Call ID not found.\n'
                f'Expr (line {self.expr.lineno}): {pretty_print.loma_to_str(self.expr)}')

class InternalError(CompileError):
    pass

@attrs.define(frozen=True)
class UnhandledDifferentiation(InternalError):
    func : loma_ir.func

    def to_string(self):
        return (f'Unhandled Differentiation.\n'
                f'Func (line {self.func.lineno}): {pretty_print.loma_to_str(self.func)}')
