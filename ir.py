from asdl_gen import ADT

def generate_asdl_file():
    ADT("""
    module loma {
      stmt = Assign     ( string target, expr val )
           | Declare    ( string target, expr val )
           | AddAssign  ( string target, expr val )
           | Declare    ( string target, expr val )
           | For        ( string target, expr start, expr stop, expr step, block body )
           | If         ( expr cond, block body )
           | Break      (  )
           | Return     ( expr val )
           attributes   ( string? attr )

      expr = Var        ( string id )
           | Const      ( float val )
           | Add        ( expr left, expr right )
           | Sub        ( expr left, expr right )
           | Mul        ( expr left, expr right )
           | Div        ( expr left, expr right )
           | Equal      ( expr left, expr right )
           attributes( string? attr )

      block    = Block ( stmt* s )
                 attributes( string? attr )

      function = Function ( string name, string* args, block body )
                 attributes( string? attr )
    }
    """,
    header= '',
    ext_types = {},
    memoize = ['Var'])
