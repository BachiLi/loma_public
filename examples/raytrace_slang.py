import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import compiler
import numpy as np
import matplotlib.pyplot as plt
import slang_utils
import slangpy

if __name__ == '__main__':
    slang_device = slang_utils.create_slang_device()
    with open('loma_code/raytrace_simd.py') as f:
        module, kernel = compiler.compile(f.read(),
                                  target = 'slang',
                                  slang_device = slang_device)

    w = 400
    h = 225
    img = slangpy.Tensor.empty(
        device=slang_device,
        dtype=module.Vec3,
        shape=(h, w)
    )

    kernel.dispatch(thread_count=[w * h, 1, 1],
                    _total_threads=w * h,
                    w = w,
                    h = h,
                    image = img.storage)
    img_np = img.to_numpy().view(np.float32)
    plt.imshow(img_np)
    plt.show()
