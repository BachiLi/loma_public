""" We use the very cool library asdl_gen to convert a 
    string ASDL definition to a hierarchy of classes.
"""

from asdl_gen import ADT

def generate_asdl_file():
    # TODO: detect if the generated file already exists
    # and if it has an earlier modification date compared to ir.py
    # if so, don't bother to generate the file

    ADT("""
    module loma {
      func = FunctionDef ( string id, arg* args, stmt* body, bool is_simd, type? ret_type )
           | ForwardDiff ( string id, string primal_func )
           | ReverseDiff ( string id, string primal_func )
             attributes  ( int? lineno )

      stmt = Assign     ( expr target, expr val )
           | Declare    ( string target, type t, expr? val )
           | Return     ( expr val )
           | IfElse     ( expr cond, stmt* then_stmts, stmt* else_stmts )
           | While      ( expr cond, int max_iter, stmt* body )
           | CallStmt   ( expr call )
           attributes   ( int? lineno )

      expr = Var          ( string id )
           | ArrayAccess  ( expr array, expr index )
           | StructAccess ( expr struct, string member_id )
           | ConstFloat   ( float val )
           | ConstInt     ( int val )
           | BinaryOp     ( bin_op op, expr left, expr right )
           | Call         ( string id, expr* args )
           attributes     ( int? lineno, type? t )

      arg  = Arg ( string id, type t, inout i )

      type = Int    ( )
           | Float  ( )
           | Array  ( type t, int? static_size )
           | Struct ( string id, struct_member* members, int? lineno )
           | Diff   ( type t )

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
    memoize = [])
