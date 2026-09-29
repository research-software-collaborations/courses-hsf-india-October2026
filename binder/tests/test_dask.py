import dask
import dask.array as da
import dask.dataframe as dd
import dask_awkward as dak
import awkward as ak
import numpy as np
import pandas as pd

print(f"dask version: {dask.__version__}")

# dask array
x = da.from_array(np.arange(1000), chunks=100)
result = x.sum().compute()
print(f"dask.array sum OK: {result}")

# dask dataframe
df = pd.DataFrame({"a": np.arange(100), "b": np.random.default_rng(0).standard_normal(100)})
ddf = dd.from_pandas(df, npartitions=4)
mean_b = ddf["b"].mean().compute()
print(f"dask.dataframe mean OK: {mean_b:.4f}")

# dask-awkward
arr = ak.Array([[1, 2, 3], [4, 5], [6]])
dask_arr = dak.from_awkward(arr, npartitions=2)
result = dak.num(dask_arr, axis=1).compute()
print(f"dask-awkward OK: lengths = {result.tolist()}")

print("PASS: dask")
