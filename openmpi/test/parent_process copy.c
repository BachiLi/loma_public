#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define NUM_CHILDREN 2

int main(int argc, char *argv[]) {
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
        MPI_Comm_spawn("child_process", MPI_ARGV_NULL, NUM_CHILDREN, info, 0, MPI_COMM_SELF, &child_comm, MPI_ERRCODES_IGNORE);

        // Communicate with children and receive responses
        for (int i = 0; i < NUM_CHILDREN; i++) {
            int child_rank;
            MPI_Recv(&child_rank, 1, MPI_INT, MPI_ANY_SOURCE, 0, child_comm, MPI_STATUS_IGNORE);
            printf("Parent received response from child process with rank %d\n", child_rank);
        }

        MPI_Info_free(&info);
    } else {
        // This should not happen since we are in singleton mode
        printf("Unexpected process in singleton mode with rank %d\n", world_rank);
    }

    MPI_Finalize();
    return 0;
}

void wrapper_return(int num_children, int* output) {
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
        MPI_Comm_spawn("child_process", MPI_ARGV_NULL, num_children, info, 0, MPI_COMM_SELF, &child_comm, MPI_ERRCODES_IGNORE);


        // Communicate with children and receive responses
        for (int i = 0; i < num_children; i++) {
            int child_rank;
            MPI_Recv(&child_rank, 1, MPI_INT, MPI_ANY_SOURCE, 0, child_comm, MPI_STATUS_IGNORE);
            printf("Parent received response from child process with rank %d\n", child_rank);
            output[i] = child_rank+20; // Store child rank in the array
        }

        MPI_Info_free(&info);
    } else {
        // This should not happen since we are in singleton mode
        printf("Unexpected process in singleton mode with rank %d\n", world_rank);
    }

    MPI_Finalize();
    // return child_ranks;
}

