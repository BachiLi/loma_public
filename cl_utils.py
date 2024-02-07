""" This file implements a thin wrapper of OpenCL API, 
mostly using the awesome library "gpuctypes"
from Geohot https://github.com/tinygrad/gpuctypes

To use the API, first you need to call the create_context function.
This will give you an OpenCL context, an OpenCL device, and an OpenCL command queue
    
    import cl_utils
    cl_ctx, cl_device, cl_cmd_queue = cl_utils.create_context()

Next, you can create an OpenCLLibrary using cl_compile

    code = ... # some OpenCL code as string
    kernel_names = [...] # names of kernels in the code you want to expose 
    lib = cl_utils.cl_compile(cl_ctx,
                              cl_device,
                              cl_cmd_queue,
                              code,
                              kernel_names)

Next, you allocate OpenCL memory buffers using clCreateBuffer

    import gpuctypes.opencl as cl
    import ctypes
    status = ctypes.c_int32()
    py_x = [0, 0, 0]
    x = (ctypes.c_int * len(py_x))(*py_x)
    bufx = cl.clCreateBuffer(cl_ctx,
                             cl.CL_MEM_WRITE_ONLY,
                             ctypes.sizeof(x),
                             ctypes.byref(x),
                             ctypes.byref(status))
    cl_utils.cl_check(status.value)

Calling lib.[function_name] gives you an OpenCLKernel object

    # f is an OpenCLKernel
    f = lib.opencl_func

Calling f(...) launches the OpenCL kernel.
You can use clFinish to wait for the kernel to complete.

    f(bufx)
    cl.clFinish(cl_cmd_queue)

Finally, use clEnqueueReadBuffer to read from the buffer

    cl.clEnqueueReadBuffer(cl_cmd_queue,
                           bufx,
                           cl.CL_TRUE,
                           0,
                           ctypes.sizeof(x),
                           ctypes.byref(x),
                           0,
                           None,
                           None)
"""

import gpuctypes.opencl as cl
import ctypes
import os

class OpenCLKernel:
    """ An OpenCLKernel wraps around a 1D OpenCL kernel.
        See the file-level comment for how it's used.
    """

    def __init__(self,
                 program,
                 func_name,
                 cmd_queue):
        self.cmd_queue = cmd_queue
        status = ctypes.c_int32()
        self.kernel = cl.clCreateKernel(program,
                                        bytes(func_name, 'utf-8'),
                                        ctypes.byref(status))
        cl_check(status.value)

    def __call__(self, *args):
        for i, buffer in enumerate(args):
            if i == len(args) - 1:
                break
            cl.clSetKernelArg(self.kernel,
                              i,
                              ctypes.sizeof(buffer),
                              ctypes.byref(buffer))
        total_work = ctypes.c_size_t(int(args[-1]))
        cl.clEnqueueNDRangeKernel(self.cmd_queue,
                                  self.kernel,
                                  1,
                                  None,
                                  ctypes.byref(total_work),
                                  None,
                                  0,
                                  None,
                                  None)

class OpenCLLibrary:
    """ An OpenCLLibrary contains many OpenCL kernels.
        See the file-level comment for how it's used.
    """

    def __init__(self,
                 program,
                 cmd_queue,
                 func_names):
        self.program = program
        self.cmd_queue = cmd_queue
        for f in func_names:
            setattr(self, f, OpenCLKernel(program, f, cmd_queue))

def to_char_p_p(options):
    c_options = (ctypes.POINTER(ctypes.c_char) * len(options))()
    c_options[:] = [ctypes.cast(ctypes.create_string_buffer(o.encode("utf-8")), ctypes.POINTER(ctypes.c_char)) for o in options]
    return c_options

def cl_check(status, info = None):
    if status != 0: raise RuntimeError(f'OpenCL Error {status}' + (('\n\n'+info) if info else ''))

def cl_get_platform_name(platform_id):
    platform_str_size = ctypes.c_size_t(0)
    cl.clGetPlatformInfo(platform_id,
                         cl.CL_PLATFORM_NAME,
                         0,
                         0,
                         ctypes.byref(platform_str_size))
    platform_str = ctypes.create_string_buffer(platform_str_size.value)
    cl.clGetPlatformInfo(platform_id,
                         cl.CL_PLATFORM_NAME,
                         platform_str_size,
                         platform_str,
                         ctypes.POINTER(ctypes.c_size_t)())
    return platform_str.value

def cl_get_device_name(device_id):
    device_str_size = ctypes.c_size_t(0)
    cl.clGetDeviceInfo(device_id,
                       cl.CL_DEVICE_NAME,
                       0,
                       0,
                       ctypes.byref(device_str_size))
    device_str = ctypes.create_string_buffer(device_str_size.value)
    cl.clGetDeviceInfo(device_id,
                       cl.CL_DEVICE_NAME,
                       device_str_size,
                       device_str,
                       ctypes.POINTER(ctypes.c_size_t)())
    return device_str.value

def create_context():
    """ Returns an OpenCL context, an OpenCL device, and an OpenCL command queue.
        It reads from the "OPENCL_CTX" environment variable to make choices.
        If the environment variable does not exist, then it interactively asks
        the user.

        See the file-level comment for how to use this.
    """

    # Some of the code is inspired from PyOpenCL https://github.com/inducer/pyopencl/

    answers = None
    if "OPENCL_CTX" in os.environ:
        ctx_spec = os.environ["OPENCL_CTX"]
        answers = [int(choice) for choice in ctx_spec.split(":")]

    # Get platforms
    num_platforms = ctypes.c_uint32()
    cl_check(cl.clGetPlatformIDs(0,
                                 ctypes.POINTER(cl.cl_platform_id)(),
                                 ctypes.byref(num_platforms)))
    platform_array = (cl.cl_platform_id * num_platforms.value)()
    cl_check(cl.clGetPlatformIDs(num_platforms,
                                 platform_array,
                                 ctypes.POINTER(ctypes.c_uint32)()))
    assert num_platforms.value > 0, 'didn\'t get platform'

    current_answers = []
    if answers is not None:
        platform = platform_array[answers[0]]
    else:
        platform_names = [cl_get_platform_name(platform_id) for platform_id in platform_array]
        print('Choose platform:')
        for i, pf in enumerate(platform_names):
            print("[%d] %s" % (i, pf))

        answer = input('Choice [0]:')
        if not answer:
            platform = platform_array[0]
            current_answers.append(0)
        else:
            platform = None
            try:
                int_choice = int(answer)
            except ValueError:
                pass
            else:
                if 0 <= int_choice < len(platform_array):
                    platform = platform_array[int_choice]

            if platform is None:
                raise RuntimeError('input did not match any platform')

            current_answers.append(int_choice)

    # Get devices
    num_devices = ctypes.c_uint32()
    cl_check(cl.clGetDeviceIDs(platform,
                               cl.CL_DEVICE_TYPE_ALL,
                               0,
                               ctypes.POINTER(cl.cl_device_id)(),
                               ctypes.byref(num_devices)))
    device_array = (cl.cl_device_id * num_devices.value)()
    cl_check(cl.clGetDeviceIDs(platform,
                               cl.CL_DEVICE_TYPE_ALL,
                               num_devices,
                               device_array,
                               ctypes.POINTER(ctypes.c_uint32)()))
    assert num_devices.value > 0, 'didn\'t get device'

    if answers is not None:
        device = device_array[answers[1]]
    else:
        device_names = [cl_get_device_name(device_id) for device_id in device_array]
        print('Choose device:')
        for i, dev in enumerate(device_names):
            print("[%d] %s" % (i, dev))

        answer = input('Choice [0]:')
        if not answer:
            device = device_array[0]
            current_answers.append(0)
        else:
            device = None
            try:
                int_choice = int(answer)
            except ValueError:
                pass
            else:
                if 0 <= int_choice < len(device_array):
                    device = device_array[int_choice]

            if device is None:
                raise RuntimeError('input did not match any device')

            current_answers.append(int_choice)

    # Create context & command queue
    status = ctypes.c_int32()
    context = cl.clCreateContext(None,
                                 num_devices,
                                 device_array,
                                 ctypes.cast(None, cl.clCreateContext.argtypes[3]),
                                 None,
                                 ctypes.byref(status))
    cl_check(status.value)
    assert context is not None

    status = ctypes.c_int32()
    cmd_queue = cl.clCreateCommandQueue(context,
                                        device,
                                        0,
                                        ctypes.byref(status))
    cl_check(status.value)

    if answers is None:
        print('Set the environment variable OPENCL_CTX=\'%s\' to '
              'avoid being asked again.' % ':'.join([str(a) for a in current_answers]))

    return context, device, cmd_queue

def cl_compile(context,
               device,
               cmd_queue,
               code,
               func_names):
    """ Compiles OpenCL programs represented as strings.
        Returns an OpenCLLibrary.
        See the file-level comment for how to use this.
    """

    num_programs = 1
    sizes = (ctypes.c_size_t * num_programs)()
    sizes[0] = len(code)
    status = ctypes.c_int32()
    program = cl.clCreateProgramWithSource(context,
                                           num_programs,
                                           to_char_p_p([code]),
                                           sizes,
                                           ctypes.byref(status))
    assert program is not None

    device_array = (cl.cl_device_id * 1)(device)
    status = cl.clBuildProgram(program,
                               1,
                               device_array,
                               None,
                               ctypes.cast(None, cl.clBuildProgram.argtypes[4]),
                               None)
    if status != 0:
        log_size = ctypes.c_size_t()
        cl.clGetProgramBuildInfo(program,
                                 device,
                                 cl.CL_PROGRAM_BUILD_LOG,
                                 0, None,
                                 ctypes.byref(log_size))
        cl.clGetProgramBuildInfo(program,
                                 device_array[0],
                                 cl.CL_PROGRAM_BUILD_LOG,
                                 log_size.value, mstr := ctypes.create_string_buffer(log_size.value), None)
        assert False, ctypes.string_at(mstr, size=log_size.value).decode()

    return OpenCLLibrary(program,
                         cmd_queue,
                         func_names)
