import slangpy
import platform

def create_slang_device():
    """
        A wrapper for generating a slang device using slangpy
        Use Metal when we're using MacOS and use SPIR-V when we're using Windows/Linux
    """
    if platform.system() == 'Darwin':
        device = slangpy.Device(type = slangpy.DeviceType.metal)
    else:
        device = slangpy.Device(type = slangpy.DeviceType.vulkan)
    return device