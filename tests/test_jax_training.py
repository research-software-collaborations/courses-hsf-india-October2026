import os
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import jax
import jax.numpy as jnp
from jax import jit, random
import optax

print(f"JAX version: {jax.__version__}")
print(f"Devices: {jax.devices()}")

def init_params(key, layer_sizes):
    params = []
    for n_in, n_out in zip(layer_sizes[:-1], layer_sizes[1:]):
        key, k1, k2 = random.split(key, 3)
        params.append({
            'w': random.normal(k1, (n_in, n_out)) * 0.01,
            'b': jnp.zeros(n_out)
        })
    return params

def forward(params, x):
    for layer in params[:-1]:
        x = jax.nn.relu(x @ layer['w'] + layer['b'])
    return x @ params[-1]['w'] + params[-1]['b']

def loss_fn(params, x, y):
    return jnp.mean((forward(params, x) - y) ** 2)

optimizer = optax.adam(1e-3)

@jit
def train_step(params, opt_state, x, y):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    updates, opt_state = optimizer.update(grads, opt_state)
    params = optax.apply_updates(params, updates)
    return params, opt_state, loss

key = random.PRNGKey(0)
x = random.normal(key, (256, 16))
y = random.normal(key, (256, 1))

params = init_params(key, [16, 64, 64, 1])
opt_state = optimizer.init(params)

for step in range(100):
    params, opt_state, loss = train_step(params, opt_state, x, y)
    if step % 20 == 0:
        print(f"step {step:3d}  loss {loss:.4f}")

print(f"Ran on: {jax.devices()[0]}")
print("PASS: jax_training")
