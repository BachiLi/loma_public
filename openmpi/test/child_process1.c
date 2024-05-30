#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

// Generated C code from loma for plus function     
typedef struct {
	float val;
	float dval;
} _dfloat;

// float plus(float x, float y);
float array_input(float* x);

// _dfloat d_plus(_dfloat x, _dfloat y);
_dfloat d_array_input(_dfloat* x);

_dfloat make__dfloat(float val, float dval);

// float plus(float x, float y) {
//     return (x) + (y);
// }
float array_input(float* x) {
    return ((x)[(int)(0)]) + ((x)[(int)(1)]);
}

// _dfloat d_plus(_dfloat x, _dfloat y) {
//     return make__dfloat(((x).val) + ((y).val),((x).dval) + ((y).dval));
// }
_dfloat d_array_input(_dfloat* x) {
        return make__dfloat((((x)[(int)(0)]).val) + (((x)[(int)(1)]).val),(((x)[(int)(0)]).dval) + (((x)[(int)(1)]).dval));
}

_dfloat make__dfloat(float val, float dval) {
    _dfloat ret;
    ret.val = 0;
    ret.dval = 0;
    (ret).val = val;
    (ret).dval = dval;
    return ret;
}

void d_array_wrapper() {
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

    int count;
    MPI_Recv(&count, 1, MPI_INT, 0, 0, parent_comm, MPI_STATUS_IGNORE);
    _dfloat* input_array = (_dfloat*)malloc(count * sizeof(_dfloat));
    if (input_array == NULL) {
        printf("Memory allocation failed\n");
        MPI_Finalize();
        return;
    }
    MPI_Recv(input_array, count * sizeof(_dfloat), MPI_BYTE, 0, 0, parent_comm, MPI_STATUS_IGNORE);
    // _dfloat x = input_array[0];
    // _dfloat y = input_array[1];
    // printf("Value %f dval: %f\n", x.val, x.dval);
    _dfloat d_addition = d_array_input(input_array);

	printf("Rank %d. d_identity Output - val: %f dval: %f\n", world_rank, d_addition.val, d_addition.dval);

    // Send rank back to parent
    MPI_Send(&d_addition, sizeof(_dfloat), MPI_BYTE, 0, 0, parent_comm);
    free(input_array);
    MPI_Finalize();
}

int main() {
    d_array_wrapper();
    return 0;
}
