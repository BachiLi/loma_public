#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct {
	float val;
	float dval;
} _dfloat;

void mpi_runner(int num_children, _dfloat input, _dfloat* output) {
    MPI_Init(NULL, NULL);

    int world_rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    if (world_rank == 0) {
        // This is the parent process
        MPI_Comm child_comm;
        MPI_Info info;
        MPI_Info_create(&info);

        // Spawn NUM_CHILDREN child processes
        MPI_Comm_spawn("child_process.o", MPI_ARGV_NULL, num_children, info, 0, MPI_COMM_SELF, &child_comm, MPI_ERRCODES_IGNORE);

        // Communicate with children and send input and receive responses
        for (int i = 0; i < num_children; i++) {
            // Send input to child process
            MPI_Send(&input, sizeof(_dfloat), MPI_BYTE, i, 0, child_comm);
        }

        // Communicate with children and receive responses
        for (int i = 0; i < num_children; i++) {
            _dfloat local_output;
            MPI_Recv(&local_output, sizeof(_dfloat), MPI_BYTE, MPI_ANY_SOURCE, 0, child_comm, MPI_STATUS_IGNORE);
            printf("Parent received response from child process with rank %f\n", local_output.val);
            output[i] = local_output; // Store child rank in the array
        }

        MPI_Info_free(&info);
    } else {
        // This should not happen since we are in singleton mode
        printf("Unexpected process in singleton mode with rank %d\n", world_rank);
    }

    MPI_Finalize();
    // return child_ranks;
}

