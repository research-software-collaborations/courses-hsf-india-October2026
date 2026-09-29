import jax
import jax.numpy as jnp
import optax
import equinox as eqx
import flax.linen as nn

print(f"optax version: {optax.__version__}")
print(f"equinox version: {eqx.__version__}")

# optax: build an optimizer and take a step
params = {"w": jnp.ones((4, 4))}
optimizer = optax.adam(1e-3)
opt_state = optimizer.init(params)
grads = {"w": jnp.ones((4, 4)) * 0.1}
updates, opt_state = optimizer.update(grads, opt_state)
new_params = optax.apply_updates(params, updates)
print(f"optax adam step OK, w[0,0]: {new_params['w'][0,0]:.6f}")

# equinox: define and call a simple MLP
class MLP(eqx.Module):
    linear: eqx.nn.Linear

    def __init__(self, key):
        self.linear = eqx.nn.Linear(4, 2, key=key)

    def __call__(self, x):
        return self.linear(x)

model = MLP(jax.random.PRNGKey(0))
out = model(jnp.ones(4))
print(f"equinox MLP OK, output shape: {out.shape}")

# flax: simple dense layer
class FlaxMLP(nn.Module):
    @nn.compact
    def __call__(self, x):
        return nn.Dense(2)(x)

model = FlaxMLP()
variables = model.init(jax.random.PRNGKey(0), jnp.ones((1, 4)))
out = model.apply(variables, jnp.ones((1, 4)))
print(f"flax Dense OK, output shape: {out.shape}")

print("PASS: jax ecosystem (optax, equinox, flax)")
