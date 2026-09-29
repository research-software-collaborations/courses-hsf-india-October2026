import jax
import jax.numpy as jnp

print(f"JAX version: {jax.__version__}")

devices = jax.devices()
gpu_devices = [d for d in devices if d.platform == "gpu"]
if gpu_devices:
    print(f"GPU: {', '.join(str(d) for d in gpu_devices)}")
else:
    print("GPU: none")

# basic jit op
@jax.jit
def matmul(a, b):
    return jnp.dot(a, b)

a = jnp.ones((128, 128))
b = jnp.ones((128, 128))
c = matmul(a, b)
print(f"JIT matmul OK, result shape: {c.shape}, sum: {c[0, 0]:.1f}")

print("PASS: jax")
