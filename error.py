import attrs as _attrs

class UserError(Exception):
    pass

@_attrs.define(frozen=True)
class DuplicateVariable(UserError):
    var : str
    first_lineno : int
    duplicate_lineno : int
