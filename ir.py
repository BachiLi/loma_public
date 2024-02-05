from asdl_gen import ADT

def generate_asdl_file():
    ADT("""
    module loma {
      func = FunctionDef ( string id, arg* args, stmt* body, bool is_simd, type? ret_type )
           | ForwardDiff ( string id, string primal_func )
           | ReverseDiff ( string id, string primal_func )
             attributes  ( int? lineno )

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
           | BinaryOp     ( bin_op op, expr left, expr right )
           | Call         ( string id, expr* args )
           attributes     ( int? lineno, type? t )

      ref = RefName   ( string id )
          | RefArray  ( ref array, expr index )
          | RefStruct ( ref struct, string member )

      arg  = Arg ( string id, type t, inout i )

      type = Int    ( )
           | Float  ( )
           | Array  ( type t, int? static_size )
           | Struct ( string id, struct_member* members, int? lineno )

      struct_member = MemberDef ( string id, type t )

      bin_op = Add()
             | Sub()
             | Mul()
             | Div()
             | Less()
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
