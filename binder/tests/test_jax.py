import jax
import jax.numpy as jnp

print(f"JAX version: {jax.__version__}")

devices = jax.devices()
print(f"JAX devices: {devices}")
gpu_devices = [d for d in devices if d.platform == "gpu"]
if gpu_devices:
    print(f"GPU available: {gpu_devices}")
else:
    print("No GPU detected by JAX — running on CPU")

# basic jit op
@jax.jit
def matmul(a, b):
    return jnp.dot(a, b)

a = jnp.ones((128, 128))
b = jnp.ones((128, 128))
c = matmul(a, b)
print(f"JIT matmul OK, result shape: {c.shape}, sum: {c[0, 0]:.1f}")

print("PASS: jax")
