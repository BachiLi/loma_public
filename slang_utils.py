import slangpy
import platform
import pathlib

def create_slang_device():
    """
        A wrapper for generating a slang device using slangpy.
        Use Metal when we're using MacOS and use SPIR-V when we're using Windows/Linux.
        For Windows machines that can't support float32 atomic add, use DirectX
        since we can use InterlockedCompareExchangeFloatBitwise to implement a 
        CAS loop.
    """
    if platform.system() == 'Darwin':
        device = slangpy.create_device(include_paths=[
                pathlib.Path(__file__).parent.absolute(),
        ], type = slangpy.DeviceType.metal)
    else:
        device = slangpy.create_device(include_paths=[
                pathlib.Path(__file__).parent.absolute(),
        ], type = slangpy.DeviceType.vulkan)
        if 'SPV_EXT_shader_atomic_float_add' not in device.capabilities and platform.system() == 'Windows':
            print('[Warning] does not detect float32 atomic add capabilities. Attempt to switch to DirectX 12')
            device = slangpy.create_device(include_paths=[
                    pathlib.Path(__file__).parent.absolute(),
            ], type = slangpy.DeviceType.d3d12)
    return device
