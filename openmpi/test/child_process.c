#include <mpi.h>
#include <stdio.h>


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

void d_identity_wrapper() {
    MPI_Init(NULL, NULL);

    MPI_Comm parent_comm;
    MPI_Comm_get_parent(&parent_comm);

    if (parent_comm == MPI_COMM_NULL) {
        printf("No parent process\n");
        MPI_Finalize();
        return;
    }

    int world_rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    _dfloat input;
    // Receive input from parent
    MPI_Recv(&input, sizeof(_dfloat), MPI_BYTE, 0, 0, parent_comm, MPI_STATUS_IGNORE);
    
	_dfloat d_iden = d_identity(input);
	printf("Rank %d. d_identity Output - val: %f dval: %f\n", world_rank, d_iden.val, d_iden.dval);

    // Send rank back to parent
    MPI_Send(&d_iden, sizeof(_dfloat), MPI_BYTE, 0, 0, parent_comm);

    MPI_Finalize();
}

int main() {
    d_identity_wrapper();
    return 0;
}
