import numpy as np
import pyopencl as cl

a_np = np.random.rand(50000).astype(np.float32)
b_np = np.random.rand(50000).astype(np.float32)
my_dtype = np.dtype([('foo', np.int32), ('bar', np.float32)])
c_np = np.empty(50000, my_dtype)

c_np[0]['foo'] = 42
c_np[0]['bar'] = 23.45

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)
c_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=c_np)

prg = cl.Program(ctx, """
typedef struct my_dtype {
  int foo;
  float bar;
} my_dtype;

float my_func() {
  return 42.f;
}

static float atomic_cmpxchg_f32(volatile __global float *p, float cmp, float val) {
  union {
    unsigned int u32;
    float        f32;
  } cmp_union, val_union, old_union;

  cmp_union.f32 = cmp;
  val_union.f32 = val;
  old_union.u32 = atomic_cmpxchg((volatile __global unsigned int *) p, cmp_union.u32, val_union.u32);
  return old_union.f32;
}

static float atomic_add_f32(volatile __global float *p, float val) {
  float found = *p;
  float expected;
  do {
    expected = found;
    found = atomic_cmpxchg_f32(p, expected, expected + val);
  } while (found != expected);
  return found;
}

__kernel void sum(
    __global const float *a_g, __global const float *b_g, __global const my_dtype *c_g, __global float *res_g)
{
  int gid = get_global_id(0);
  res_g[gid] = a_g[gid] + b_g[gid] + c_g[0].foo + my_func();
  atomic_add_f32(&res_g[gid], 1.0f);
}
""").build()

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)
knl = prg.sum  # Use this Kernel object for repeated calls
knl(queue, a_np.shape, None, a_g, b_g, c_g, res_g)

res_np = np.empty_like(a_np)
cl.enqueue_copy(queue, res_np, res_g)

# Check on CPU with Numpy:
print(res_np - (a_np + b_np))
print(np.linalg.norm(res_np - (a_np + b_np)))
assert np.allclose(res_np, a_np + b_np)
