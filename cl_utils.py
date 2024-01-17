import gpuctypes.opencl as cl
import ctypes
import os

class OpenCLKernel:
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
