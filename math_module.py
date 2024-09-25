import numpy as np
import scipy

try:
    import cupy
    import cupyx.scipy
    cupy_avail = True
except ImportError:
    print('Cupy unavailable; computations will not be performed using GPU with CuPy.')
    cupy_avail = False

class np_backend:
    """A shim that allows a backend to be swapped at runtime."""
    def __init__(self, src):
        self._srcmodule = src

    def __getattr__(self, key):
        if key == '_srcmodule':
            return self._srcmodule

        return getattr(self._srcmodule, key)
    
class scipy_backend:
    """A shim that allows a backend to be swapped at runtime."""
    def __init__(self, src):
        self._srcmodule = src

    def __getattr__(self, key):
        if key == '_srcmodule':
            return self._srcmodule

        return getattr(self._srcmodule, key)
    
if cupy_avail:
    xp = np_backend(cupy)
    xcipy = scipy_backend(cupyx.scipy)
else:
    xp = np_backend(np)
    xcipy = scipy_backend(scipy)

def update_xp(module):
    xp._srcmodule = module
    
def update_scipy(module):
    xcipy._srcmodule = module
    
def  np_array(arr):
    if isinstance(arr, np.ndarray):
        return arr
    elif cupy_avail and isinstance(arr, cupy.ndarray):
        return arr.get()

