import numba
import numpy as np

print(f"numba version: {numba.__version__}")

# check CUDA availability
try:
    from numba import cuda
    if cuda.is_available():
        gpu = cuda.get_current_device()
        print(f"GPU: {gpu.name}")
    else:
        print("GPU: none")
except Exception as e:
    print(f"GPU: none (error: {e})")

# basic JIT
@numba.njit
def sum_array(arr):
    total = 0.0
    for v in arr:
        total += v
    return total

arr = np.arange(1000, dtype=np.float64)
result = sum_array(arr)
print(f"numba @njit OK: sum = {result:.0f}")

print("PASS: numba")
