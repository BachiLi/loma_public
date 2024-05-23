import codegen_c
import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir
import compiler

class OpemMpiCodegenVisitor(codegen_c.CCodegenVisitor):
    """ Generates MPI code from loma IR.
        See https://ispc.github.io/index.html for more details about ispc.
    """

    def __init__(self, func_defs):
        super().__init__(func_defs)

    def visit_function_def(self, node: loma_ir.FunctionDef):
        self.code += f'{codegen_c.type_to_string(node.ret_type)} {node.id}('
        for i, arg in enumerate(node.args):
            if i > 0:
                self.code += ', '
            self.code += f'{codegen_c.type_to_string(arg)} {arg.id}'
        if node.is_simd:
            if len(node.args) > 0:
                self.code += ', '
            self.code += 'int __total_work'
        self.code += ') {\n'
        self.byref_args = set([arg.id for arg in node.args if \
            arg.i == loma_ir.Out() and (not isinstance(arg.t, loma_ir.Array))])

        self.tab_count += 1
        if node.is_simd:
            self.emit_tabs()
            self.code += 'for (int __work_id = 0; __work_id < __total_work; __work_id++) {\n'
            self.tab_count += 1
        for stmt in node.body:
            self.visit_stmt(stmt)
        if node.is_simd:
            self.tab_count -= 1
            self.emit_tabs()
            self.code += '}\n'
        self.tab_count -= 1
        self.code += '}\n'

        ## openMpi code
        if node.is_openMpi and node.id.startswith("d_"):
            new_node_id = node.id + '_mpi_worker'
            self.code += f'void {new_node_id}()'

            self.code += '{\n'
            self.code += """
    MPI_Init(NULL, NULL);

    MPI_Comm parent_comm;
    MPI_Comm_get_parent(&parent_comm);

    if (parent_comm == MPI_COMM_NULL) {
        MPI_Finalize();
        return;
    }

    int world_rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    """
            self.code += f"""
    {node.args[0].t.id} input;
    MPI_Recv(&input, sizeof({node.args[0].t.id}), MPI_BYTE, 0, 0, parent_comm, MPI_STATUS_IGNORE);
    """
            self.code += f"{codegen_c.type_to_string(node.ret_type)} out = {node.id}(input);\n"
            self.code += f"""
    MPI_Send(&out, sizeof({codegen_c.type_to_string(node.ret_type)}), MPI_BYTE, 0, 0, parent_comm);

    MPI_Finalize();
"""

            self.tab_count -= 1
            self.code += '}\n'

            ## Write main function
            self.code += f"""
int main() {{
    {new_node_id}();
    return 0;
}}
"""
            
    def create_parent_code(self, node: loma_ir.FunctionDef, output_filename: str):
        new_node_id = node.id + '_mpi_worker'
        self.code += f"""
void mpi_runner( """
        for i, arg in enumerate(node.args):
            if i > 0:
                self.code += ', '
            self.code += f'{codegen_c.type_to_string(arg)} {arg.id}'

        self.code += f""", {codegen_c.type_to_string(node.ret_type)}* output, int __total_work) {{
    MPI_Init(NULL, NULL);

    int world_rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    if (world_rank == 0) {{
        // This is the parent process
        MPI_Comm child_comm;
        MPI_Info info;
        MPI_Info_create(&info);

        // Spawn NUM_CHILDREN child processes
        MPI_Comm_spawn("{output_filename}", MPI_ARGV_NULL, __total_work, info, 0, MPI_COMM_SELF, &child_comm, MPI_ERRCODES_IGNORE);

        for (int i = 0; i < __total_work; i++) {{
            // Send input to child process
            MPI_Send(&{node.args[0].id}, sizeof({node.args[0].t.id}), MPI_BYTE, i, 0, child_comm);
        }}

        // Communicate with children and receive responses
        for (int i = 0; i < __total_work; i++) {{
            _dfloat local_output;
            MPI_Recv(&local_output, sizeof(_dfloat), MPI_BYTE, MPI_ANY_SOURCE, 0, child_comm, MPI_STATUS_IGNORE);
            output[i] = local_output;
        }}

        MPI_Info_free(&info);
    }}

    MPI_Finalize();
}}"""

def codegen_openMpiChild(structs : dict[str, loma_ir.Struct],
                 funcs : dict[str, loma_ir.func],
                 ) -> str:
    """ Given loma Structs (structs) and loma functions (funcs),
        return a string that represents the equivalent ISPC code.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
    """

    sorted_structs_list = compiler.topo_sort_structs(structs)

    # Definition of structs
    code = ''
    for s in sorted_structs_list:
        code += f'typedef struct {{\n'
        for m in s.members:
            # Special rule for arrays
            if isinstance(m.t, loma_ir.Array) and m.t.static_size is not None:
                code += f'\t{codegen_c.type_to_string(m.t.t)} {m.id}[{m.t.static_size}];\n'
            else:
                code += f'\t{codegen_c.type_to_string(m.t)} {m.id};\n'
        code += f'}} {s.id};\n'

    # Forward declaration of functions
    for f in funcs.values():
        code += f'{codegen_c.type_to_string(f.ret_type)} {f.id}('
        for i, arg in enumerate(f.args):
            if i > 0:
                code += ', '
            code += f'{codegen_c.type_to_string(arg)} {arg.id}'
        if f.is_simd:
            if len(f.args) > 0:
                code += ', '
            code += 'int __total_work'
        code += ');\n'

    for f in funcs.values():
        cg = OpemMpiCodegenVisitor(funcs)
        cg.visit_function(f)
        code += cg.code
    return code


def codegen_openMpiParent(structs : dict[str, loma_ir.Struct],
                 funcs : dict[str, loma_ir.func],
                 output_filename: str) -> str:
    """ Given loma Structs (structs) and loma functions (funcs),
        return a string that represents the equivalent ISPC code.

        Parameters:
        structs - a dictionary that maps the ID of a Struct to 
                the corresponding Struct
        funcs - a dictionary that maps the ID of a function to 
                the corresponding func
    """

    sorted_structs_list = compiler.topo_sort_structs(structs)

    # Definition of structs
    code = ''
    for s in sorted_structs_list:
        code += f'typedef struct {{\n'
        for m in s.members:
            # Special rule for arrays
            if isinstance(m.t, loma_ir.Array) and m.t.static_size is not None:
                code += f'\t{codegen_c.type_to_string(m.t.t)} {m.id}[{m.t.static_size}];\n'
            else:
                code += f'\t{codegen_c.type_to_string(m.t)} {m.id};\n'
        code += f'}} {s.id};\n'

    to_call_f = [f for f in funcs.values() if f.is_openMpi and f.id.startswith("d_")]
    cg = OpemMpiCodegenVisitor(funcs)
    if len(to_call_f) == 1:
        cg.create_parent_code(to_call_f[0], output_filename)
    code += cg.code
    return code