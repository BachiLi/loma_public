import ast
import attrs
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import pretty_print

class UserError(Exception):
    pass

@attrs.define(frozen=True)
class FuncArgNotAnnotated(UserError):
    node : ast.AST # Python AST Node

    def to_string(self):
        return (f'[Error] Function argument not annotated as In/Out.\n'
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
        return (f'[Error] Duplicated variable declaration detected.\n'
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
        return (f'[Error] Undeclared variable use detected.\n'
                f'Variable name: {self.var}.\n'
                f'Statement/Expr (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class ReturnNotLastStmt(UserError):
    # the return statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'[Error] Return is not the last statement, or is inside an if/while statement.\n'
                f'Statement (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class DeclareUnboundedArray(UserError):
    # the declare statement
    stmt : loma_ir.stmt

    def to_string(self):
        return (f'[Error] Variable declaration with unbounded size detected.\n'
                f'Statement (line {self.stmt.lineno}): {pretty_print.loma_to_str(self.stmt)}')

@attrs.define(frozen=True)
class ArrayAccessTypeMismatch(UserError):
    # line number where the array access happens
    lineno : int

@attrs.define(frozen=True)
class StructAccessTypeMismatch(UserError):
    # line number where the struct access happens
    lineno : int

@attrs.define(frozen=True)
class StructMemberNotFound(UserError):
    # line number where the struct access happens
    lineno : int

@attrs.define(frozen=True)
class BinaryOpTypeMismatch(UserError):
    # line number where the binary op happens
    lineno : int

@attrs.define(frozen=True)
class CallTypeMismatch(UserError):
    # The function ID of the call
    call_id : str
    # line number where the call op happens
    lineno : int

@attrs.define(frozen=True)
class ReturnTypeMismatch(UserError):
    # line number where the return op happens
    lineno : int

@attrs.define(frozen=True)
class AssignTypeMismatch(UserError):
    # line number where the assign op happens
    lineno : int

@attrs.define(frozen=True)
class DeclareTypeMismatch(UserError):
    # line number where the declare op happens
    lineno : int

@attrs.define(frozen=True)
class IfElseCondTypeMismatch(UserError):
    # line number where the IfElse op happens
    lineno : int

@attrs.define(frozen=True)
class CallIDNotFound(UserError):
    # The function ID of the call
    call_id : str
    # line number where the call op happens
    lineno : int

class InternalError(Exception):
    pass

@attrs.define(frozen=True)
class UnhandledDifferentiation(InternalError):
    # ID of the derivative function
    diff_func_id : str
    # line number where the differentiation is declared
    lineno : int
