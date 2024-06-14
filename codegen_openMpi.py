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
        reverse_diff = False
        self.code += f'{codegen_c.type_to_string(node.ret_type)} {node.id}('
        for i, arg in enumerate(node.args):
            if '_d' in arg.id:
                reverse_diff = True
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
        self.forward_out_args = set([arg.id for arg in node.args if arg.i == loma_ir.Out() and (isinstance(arg.t, loma_ir.Array))])
        
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
            for arg in node.args:
                if arg.id in self.byref_args:
                    self.code += f"{codegen_c.type_to_string(arg.t)} {arg.id};\n"
                elif isinstance(arg.t,loma_ir.Array):
                    self.code += f"int {arg.id}_size;\n"
                    self.code += f"MPI_Recv(&{arg.id}_size, 1, MPI_INT, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                    if isinstance(arg.t.t,loma_ir.Int):
                        self.code += f"int* {arg.id} = (int*)malloc({arg.id}_size * sizeof(int));"
                        self.code += f"MPI_Recv({arg.id}, {arg.id}_size * sizeof(int), MPI_INT, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                    else:
                        if reverse_diff:
                            self.code += f"float* {arg.id} = (float*)malloc({arg.id}_size * sizeof(float));"
                            self.code += f"MPI_Recv({arg.id}, {arg.id}_size * sizeof(float), MPI_BYTE, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                        else:
                            self.code += f"_dfloat* {arg.id} = (_dfloat*)malloc({arg.id}_size * sizeof(_dfloat));"
                            self.code += f"MPI_Recv({arg.id}, {arg.id}_size * sizeof(_dfloat), MPI_BYTE, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                #     self.code += f"""
                # for(int g=0;g<{arg.id}_size;g++){{
                #     printf("Value: %d, Dvalue: %d \\n", {arg.id}[g].val,{arg.id}[g].dval);
                # }}
                # """
                    # self.code += f"_dfloat* {arg.id} = (_dfloat*)malloc(4* sizeof(_dfloat));"
                    # self.code += f"MPI_Recv({arg.id}, sizeof(_dfloat)*4, MPI_BYTE, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                elif isinstance(arg.t,loma_ir.Int):
                    self.code += f"int {arg.id};\n"
                    self.code += f"MPI_Recv(&{arg.id}, 1, MPI_INT, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                elif isinstance(arg.t,loma_ir.Float):
                    self.code += f"float {arg.id};\n"
                    self.code += f"MPI_Recv(&{arg.id}, 1, MPI_FLOAT, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
                else:
                    self.code += f"{codegen_c.type_to_string(arg.t)} {arg.id};\n"
                    self.code += f"MPI_Recv(&{arg.id}, sizeof({arg.id}), MPI_BYTE, 0, 0, parent_comm,MPI_STATUS_IGNORE);\n"
            
            temp_string = ''
            for i, arg in enumerate(node.args):
                if i > 0:
                    temp_string += ', '
                if arg.id in self.byref_args:
                    temp_string += f"&{arg.id}"
                else:
                    temp_string += f'{arg.id}'
            temp_string += ");"
            if codegen_c.type_to_string(node.ret_type) == "void":
                self.code += f"{node.id}("
                self.code += temp_string
                for arg in node.args:
                    if arg.id in self.forward_out_args:
                        self.code += f"MPI_Send(&{arg.id}_size, 1, MPI_INT, 0, 0, parent_comm);\n"
                        if reverse_diff:
                            self.code += f"MPI_Send({arg.id}, {arg.id}_size * sizeof(float), MPI_BYTE, 0, 0, parent_comm);\n"
                        else:
                            self.code += f"MPI_Send({arg.id}, {arg.id}_size * sizeof(_dfloat), MPI_BYTE, 0, 0, parent_comm);\n"
            else:
                self.code += f"{codegen_c.type_to_string(node.ret_type)} out = {node.id}("
                self.code += temp_string
                self.code += f"""
                MPI_Send(&out, sizeof({codegen_c.type_to_string(node.ret_type)}), MPI_BYTE, 0, 0, parent_comm);
                """
            for arg in node.args:
                if arg.id in self.byref_args:
                    if isinstance(arg.t,loma_ir.Int):
                        self.code+=f"""MPI_Send(&{arg.id}, 1, MPI_INT, 0, 0, parent_comm);"""
                    elif isinstance(arg.t,loma_ir.Float):
                        self.code += f"MPI_Send(&{arg.id}, 1, MPI_FLOAT, 0, 0, parent_comm);\n"
                    else:
                       self.code += f"MPI_Send(&{arg.id}, sizeof({codegen_c.type_to_string(node.ret_type)}), MPI_BYTE, 0, 0, parent_comm);"

            self.code += """\nMPI_Finalize();"""
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
        reverse_diff = False
        array_number = 0
        self.byref_args = set([arg.id for arg in node.args if \
            arg.i == loma_ir.Out() and (not isinstance(arg.t, loma_ir.Array))])
        self.forward_out_args = set([arg.id for arg in node.args if arg.i == loma_ir.Out() and (isinstance(arg.t, loma_ir.Array))])
        new_node_id = node.id + '_mpi_worker'
        self.code += "void mpi_runner("
        for i, arg in enumerate(node.args):

            if '_d' in arg.id:
                reverse_diff = True
            if i > 0:
                self.code += ', '
            if isinstance(arg.t, loma_ir.Array):
                self.code += f'{codegen_c.type_to_string(arg)} {arg.id}'
                self.code += f',int* {arg.id}_size'
                array_number +=1
            elif arg.id in self.byref_args:
                self.code += f'{codegen_c.type_to_string(arg)} {arg.id}'
            else:
                self.code += f'{codegen_c.type_to_string(arg)}* {arg.id}'            
        if len(node.args) > 0:
            self.code += ', '
        if codegen_c.type_to_string(node.ret_type) != 'void':
            self.code += f'{codegen_c.type_to_string(node.ret_type)}* output, '
        self.code += 'int __total_work'
        self.code += ') {\n'
    
        self.code += f"""
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
        int* array_end = (int*)malloc({array_number} * sizeof(int));
        int end = 0;
        int array_index = 0;
        for (int i = 0; i< {array_number};i++){{
            array_end[i] = 0;
        }}
        for (int i = 0; i < __total_work; i++) {{   
            array_index = 0;
            // Send input to child process
            """
        for arg in node.args:
            if arg.id in self.byref_args:
                continue
            if isinstance(arg.t,loma_ir.Array):            
                self.code += f"MPI_Send(&{arg.id}_size[i], 1, MPI_INT, i, 0, child_comm);\n"
                if isinstance(arg.t.t,loma_ir.Int):
                   self.code += f""" 
                int* {arg.id}_i = (int*)malloc({arg.id}_size[i] * sizeof(int)); 
                """
                else:
                    if reverse_diff:
                        self.code += f""" 
                        float* {arg.id}_i = (float*)malloc({arg.id}_size[i] * sizeof(float)); 
                    """
                    else:
                        self.code += f""" 
                    _dfloat* {arg.id}_i = (_dfloat*)malloc({arg.id}_size[i] * sizeof(_dfloat)); 
                    """
                self.code += f"""
                end = array_end[array_index];
                for (int j = 0; j < {arg.id}_size[i]; j++) {{
                    {arg.id}_i[j] = {arg.id}[end++];
                }}
                array_end[array_index] = end;
                array_index = array_index + 1;
                """
                if reverse_diff:
                    self.code += f"MPI_Send({arg.id}_i, sizeof(float)*{arg.id}_size[i], MPI_BYTE, i, 0, child_comm);\n"
                else:
                    self.code += f"MPI_Send({arg.id}_i, sizeof(_dfloat)*{arg.id}_size[i], MPI_BYTE, i, 0, child_comm);\n"
                
            elif isinstance(arg.t,loma_ir.Int):
                self.code += f"MPI_Send(&{arg.id}[i], 1, MPI_INT, i, 0, child_comm);\n"
            elif isinstance(arg.t,loma_ir.Float):
                self.code += f"MPI_Send(&{arg.id}[i], 1, MPI_FLOAT, i, 0, child_comm);\n"
            else:
                self.code += f"MPI_Send(&{arg.id}[i], sizeof({arg.id}[i]), MPI_BYTE, i, 0, child_comm);\n"
        
        self.code += "}\n"
        tmp_string = ''
        for args in node.args:
            if args.id in self.byref_args:
                tmp_string+= f"{codegen_c.type_to_string(args.t)} _temp_{args.id};"
                if isinstance(args.t,loma_ir.Int):
                    tmp_string += f"MPI_Recv(&_temp_{args.id}, 1, MPI_INT, i, 0, child_comm, MPI_STATUS_IGNORE);\n"
                elif isinstance(args.t,loma_ir.Float):
                    tmp_string += f"MPI_Recv(&_temp_{args.id}, 1, MPI_FLOAT, i, 0, child_comm, MPI_STATUS_IGNORE);\n"
                else:
                    tmp_string += f"MPI_Recv(&_temp_{args.id}, 1, sizeof({codegen_c.type_to_string(node.ret_type)}), i, 0, child_comm, MPI_STATUS_IGNORE);\n"
                tmp_string += f"{args.id}[i] = _temp_{args.id};\n" 
            elif args.id in self.forward_out_args:
                tmp_string += f"int {args.id}_size_recv;\n"
                tmp_string += f"MPI_Recv(&{args.id}_size_recv, 1, MPI_INT, i, 0, child_comm, MPI_STATUS_IGNORE);\n"
                if reverse_diff:
                    tmp_string += f"float* {args.id}_temp = (float*)malloc({args.id}_size_recv * sizeof(float));"
                    tmp_string += f"MPI_Recv({args.id}_temp, {args.id}_size_recv* sizeof(float), MPI_BYTE, i, 0, child_comm,MPI_STATUS_IGNORE);\n"
                else:
                    tmp_string += f"_dfloat* {args.id}_temp = (_dfloat*)malloc({args.id}_size_recv * sizeof(_dfloat));"
                    tmp_string += f"MPI_Recv({args.id}_temp, {args.id}_size_recv* sizeof(_dfloat), MPI_BYTE, i, 0, child_comm,MPI_STATUS_IGNORE);\n"
                tmp_string += f"""
                rend = rec_end[rec_array_index];
                for (int j = 0; j < {args.id}_size_recv; j++) {{
                    {args.id}[rend] = {args.id}_temp[j];
                    rend++;
                }}
                rec_end[rec_array_index] = rend;
                rec_array_index = rec_array_index + 1;
                """
        if codegen_c.type_to_string(node.ret_type) != "void":
            self.code += f""" 
            // Communicate with children and receive responses
            for (int i = 0; i < __total_work; i++) {{
                {codegen_c.type_to_string(node.ret_type)} local_output;
                MPI_Recv(&local_output, sizeof({codegen_c.type_to_string(node.ret_type)}), MPI_BYTE, i, 0, child_comm, MPI_STATUS_IGNORE);
                {tmp_string}
                output[i] = local_output;        
            }}
            MPI_Info_free(&info);
        }} 
        MPI_Finalize();
    }}"""
        else:
            self.code += f""" 
            // Communicate with children and receive responses
            int* rec_end = (int*)malloc({array_number} * sizeof(int));
            int rend = 0;
            int rec_array_index = 0;
            for (int i = 0; i< {array_number};i++){{
                rec_end[i] = 0;
            }}
            for (int i = 0; i < __total_work; i++) {{
                rec_array_index = 0;
                {tmp_string}        
            }}
            """
            self.code += """MPI_Info_free(&info);} MPI_Finalize();}"""
        
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