#include "mpi.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <math.h>


// Generated C code from loma for identity function     
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
	return make__dfloat((x).val,(x).dval);
}

_dfloat make__dfloat(float val, float dval) {
	_dfloat ret;
	ret.val = 0;
	ret.dval = 0;
	(ret).val = val;
	(ret).dval = dval;
	return ret;
}

int main (int argc, char **argv)
{
    _dfloat* results = NULL;
    mpi_runner(argc, argv, &results);
    if (results != NULL) {
        for (int i = 0; i < 4; i++) {
                printf("Node %d: val = %f, dval = %f\n", i, results[i].val, results[i].dval);
        }
    }

    return 0;
}

void mpi_runner(int argc, char **argv, _dfloat** resultsFinal) {

    int perform_launch = 0;

    // Scan argv[] for special option like "-launchmpi"
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-launchmpi") == 0) {
            perform_launch = 1;
            break;
        }
    }
    printf("perform_launch: %d\n", perform_launch);

    if (perform_launch)
    {
        // #args = argc + 3 ("mpirun -np 4" added) + NULL
        // #args should be reduced by one if "-launchmpi" is present
        int new_argc = argc + 3;
        char **args = (char **)calloc(new_argc, sizeof(char *));
        args[0] = "mpirun";
        args[1] = "-np";
        args[2] = "4";
        args[3] = argv[0];

        for (int i = 0; i < new_argc; i++) {
            printf("args: %s\n", args[i]);
        }

        execvp("mpirun", args);
        
        // If execvp returns, an error occurred
        perror("execvp failed");
        free(args);
    }

    int size;
    _dfloat* results;

    mpi_wrapper(argc, argv, &size, &results);

    if (results != NULL) {
        *resultsFinal = results;
    }
}

int mpi_wrapper(int argc, char **argv, int* size, _dfloat** gatherresult) {

    int rank;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, size);

    // Variable to store the result from each node
    _dfloat local_result;
    _dfloat d_x = {rank, 0.0};
    local_result = d_identity(d_x);
    printf("Rank %d. d_identity Output - val: %f dval: %f\n", rank, local_result.val, local_result.dval);

    // // Array to collect results from all nodes
    _dfloat* all_results = NULL;
    if (rank == 0) {
        all_results = (_dfloat*)malloc((*size) * sizeof(_dfloat));
    }

    // // Gather results from all nodes to the root node
    MPI_Gather(&local_result, 2, MPI_FLOAT, all_results, 2, MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Finalize MPI
    MPI_Finalize();

    *gatherresult = all_results;
}