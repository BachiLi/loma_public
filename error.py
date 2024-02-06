import attrs

class UserError(Exception):
    pass

@attrs.define(frozen=True)
class DuplicateVariable(UserError):
    # the name of the variable that is duplicated
    var : str
    # the line number where the variable is first declared
    first_lineno : int
    # the line number where the variable is duplicatedly declared
    duplicate_lineno : int

@attrs.define(frozen=True)
class UndeclaredVariable(UserError):
    # the name of the variable that is undeclared
    var : str
    # line number where the variable is assigned
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
