import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

def differentiate(structs, funcs):
    funcs_to_be_diffed = False
    for f in funcs:
        if isinstance(f, loma_ir.ForwardDiff) or isinstance(f, loma_ir.ReverseDiff):
            funcs_to_be_diffed = True

    if not funcs_to_be_diffed:
        return structs, funcs

    # HW1 TODO: add structs for the differential types
    # (including float)

    # HW1 TODO: handle ForwardDiff for straight-line code

    return structs, funcs
