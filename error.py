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

