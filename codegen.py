import codegen_c

def codegen(structs, funcs):
    return codegen_c.codegen_c(structs, funcs)
