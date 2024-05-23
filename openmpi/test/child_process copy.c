#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int world_rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    printf("Child process started with rank %d out of %d\n", world_rank, world_size);

    // Send rank back to parent
    MPI_Comm parent_comm;
    MPI_Comm_get_parent(&parent_comm);
    if (parent_comm != MPI_COMM_NULL) {
        MPI_Send(&world_rank, 1, MPI_INT, 0, 0, parent_comm);
    } else {
        printf("No parent found for child process %d\n", world_rank);
    }

    MPI_Finalize();
    return 0;
}

