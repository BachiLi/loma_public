from asdl_gen import ADT

def generate_asdl_file():
    ADT("""
    module loma {
      stmt = Assign     ( string target, expr val, expr? index )
           | Declare    ( string target, type t, expr val )
           | Return     ( expr val )
           | IfElse     ( expr cond, stmt* then_stmts, stmt* else_stmts )
           | While      ( expr cond, stmt* body )
           attributes   ( int? lineno, string? attr )

      expr = Var         ( string id )
           | ArrayAccess ( string id, expr index )
           | ConstFloat  ( float val )
           | ConstInt    ( int val )
           | Add         ( expr left, expr right )
           | Sub         ( expr left, expr right )
           | Mul         ( expr left, expr right )
           | Div         ( expr left, expr right )
           | Compare     ( cmp_op op, expr left, expr right )
           | Call        ( string id, expr* args )
           attributes    ( int? lineno, string? attr, type? t )

      function = Function ( string name, arg* args, stmt* body, type? ret_type)
                 attributes( int? lineno, string? attr )

      arg  = Arg ( string id, type t, inout i )

      type = Int()
           | Float()
           | Array( type t )

      cmp_op = Less()
             | LessEqual()
             | Greater()
             | GreaterEqual()
             | Equal()
             | And()
             | Or()

      inout = In() | Out()
    }
    """,
    header= '',
    ext_types = {},
    memoize = ['Var'])
