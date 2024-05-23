#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    float val;
    float dval;
} _dfloat;

float identity(float x);

_dfloat d_identity(_dfloat x);

_dfloat make__dfloat(float val, float dval);

float identity(float x) {
    return x;
}

_dfloat d_identity(_dfloat x) {
    return make__dfloat(x.val, x.dval);
}

_dfloat make__dfloat(float val, float dval) {
    _dfloat ret;
    ret.val = val;
    ret.dval = dval;
    return ret;
}

int main(int argc, char** argv) {
    // Print the number of arguments
    printf("Number of arguments (argc): %d\n", argc);

    // Loop through each argument and print it
    for (int i = 0; i < argc; i++) {
        printf("Argument %d (argv[%d]): %s\n", i, i, argv[i]);
    }

    // Initialize MPI interface
    MPI_Init(&argc, &argv);

    // Rank corresponds to number of nodes
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // General C code
    float x = rank;
    float iden = identity(rank);
    printf("Rank %d. identity Output - %f\n", rank, iden);

    // Loma Code
    _dfloat d_x = {rank, 0.0};
    _dfloat d_iden = d_identity(d_x);
    printf("Rank %d. d_identity Output - val: %f dval: %f\n", rank, d_iden.val, d_iden.dval);

    // Gather d_iden values to the root process
    _dfloat* gathered_d_iden = NULL;
    if (rank == 0) {
        gathered_d_iden = (_dfloat*)malloc(size * sizeof(_dfloat));
    }

    MPI_Gather(&d_iden, 2, MPI_FLOAT, gathered_d_iden, 2, MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Print gathered results at the root
    if (rank == 0) {
        for (int i = 0; i < size; i++) {
            printf("Gathered from rank %d: val = %f, dval = %f\n", i, gathered_d_iden[i].val, gathered_d_iden[i].dval);
        }
    }

    // Terminate MPI execution environment
    MPI_Finalize();
    return 0;
}
