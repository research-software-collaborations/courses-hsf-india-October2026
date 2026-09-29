import awkward as ak
import hist
import vector
import particle
import uproot
import numpy as np

print(f"awkward version: {ak.__version__}")
print(f"hist version: {hist.__version__}")
print(f"vector version: {vector.__version__}")
print(f"particle version: {particle.__version__}")
print(f"uproot version: {uproot.__version__}")

# awkward arrays
arr = ak.Array([[1, 2, 3], [4, 5], [6]])
print(f"awkward Array OK: {ak.sum(arr)} = 21")

# vector: Lorentz 4-vectors
vector.register_awkward()
vecs = ak.Array([{"px": 1.0, "py": 0.0, "pz": 0.0, "energy": 2.0},
                 {"px": 0.0, "py": 1.0, "pz": 0.0, "energy": 2.0}],
                with_name="Momentum4D")
print(f"vector 4-momentum OK: mass = {vecs[0].mass:.4f}")

# hist: fill a 1D histogram
h = hist.Hist(hist.axis.Regular(10, 0, 1, name="x"))
h.fill(x=np.random.default_rng(0).uniform(size=1000))
print(f"hist fill OK: {h.sum():.0f} entries")

# particle: look up the pion
pi = particle.Particle.from_pdgid(211)
print(f"particle PDG OK: {pi.name}, mass = {pi.mass:.4f} MeV")

# uproot: write and read back a tiny file
import tempfile, os
with tempfile.NamedTemporaryFile(suffix=".root", delete=False) as f:
    fname = f.name
try:
    with uproot.recreate(fname) as f:
        f["tree"] = {"x": np.array([1.0, 2.0, 3.0])}
    with uproot.open(fname) as f:
        vals = f["tree/x"].array(library="np")
    assert list(vals) == [1.0, 2.0, 3.0], vals
    print(f"uproot write/read OK: {vals}")
finally:
    os.unlink(fname)

print("PASS: hep stack (awkward, hist, vector, particle, uproot)")
