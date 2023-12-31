from asdl_gen import ADT

def generate_asdl_file():
    ADT("""
    module loma {
      stmt = Assign     ( ref target, expr val )
           | Declare    ( string target, type t, expr? val )
           | Return     ( expr val )
           | IfElse     ( expr cond, stmt* then_stmts, stmt* else_stmts )
           | While      ( expr cond, stmt* body )
           attributes   ( int? lineno )

      expr = Var          ( string id )
           | ArrayAccess  ( ref array, expr index )
           | StructAccess ( ref struct, string member_id )
           | ConstFloat   ( float val )
           | ConstInt     ( int val )
           | Add          ( expr left, expr right )
           | Sub          ( expr left, expr right )
           | Mul          ( expr left, expr right )
           | Div          ( expr left, expr right )
           | Compare      ( cmp_op op, expr left, expr right )
           | Call         ( string id, expr* args )
           attributes     ( int? lineno, type? t )

      ref = RefName   ( string id )
          | RefArray  ( ref array, expr index )
          | RefStruct ( ref struct, string member )

      func = FunctionDef ( string id, arg* args, stmt* body, bool is_simd, type? ret_type)
             attributes  ( int? lineno )

      arg  = Arg ( string id, type t, inout i )

      type = Int    ( )
           | Float  ( )
           | Array  ( type t, int? static_size )
           | Struct ( string id, struct_member* members, int? lineno )

      struct_member = MemberDef ( string id, type t )

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
