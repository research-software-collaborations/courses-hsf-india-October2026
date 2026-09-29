# Binder Setup Guide

How to create/update the `binder` branch for a new course repo by merging configurations from previous course branches.

## 1. Check source branches for binder configs

```bash
# List branches in the previous repo
gh api repos/research-software-collaborations/<PREV-REPO>/branches | jq '.[].name'

# See what binder files each branch has
gh api "repos/research-software-collaborations/<PREV-REPO>/git/trees/<BRANCH>?recursive=1" \
  | jq '.tree[] | select(.path | contains("binder")) | .path'

# Read a file from a branch
gh api "repos/research-software-collaborations/<PREV-REPO>/contents/binder/environment.yml?ref=<BRANCH>" \
  | jq -r '.content' | base64 -d
```

## 2. Merge environment.yml files

Combine the conda `dependencies` lists from each source branch, then:

- **Deduplicate** packages that appear in both
- **JAX ecosystem** (`jax`, `jaxlib`, `optax`, `equinox`, `flax`): always install via **pip** using `jax[cuda13]` (or the matching cuda version) to avoid a jaxlib conflict where conda and pip each install their own copy
- **PyTorch**: use `pytorch-gpu` from conda-forge for the CUDA-enabled build. Do **not** use the `pytorch` anaconda channel — it is deprecated and stalled at CUDA 12.4
- **servicex**: install via pip — its `qastle` dependency is not in conda channels
- **numpy pin** (`numpy<2`): comment out unless you know all packages need it; note which branch it came from
- Set the **channel** to match the CUDA version: `nvidia/label/cuda-X.Y`

## 3. Choose the CUDA version

Check what the host cluster driver supports:
```bash
nvidia-smi  # top-right corner shows "CUDA Version: X.Y"
```
Use that version (or lower) for `CONDA_OVERRIDE_CUDA` in the Dockerfile and the nvidia channel in `environment.yml`. The driver is **backward compatible**, so a container built for an older CUDA version will still work after a driver upgrade.

## 4. Check for newer package versions

```bash
# micromamba
gh api repos/mamba-org/mamba/releases?per_page=5 | jq '.[].tag_name'
# Note: setup-micromamba action requires format X.Y.Z-0 (with build number suffix)

# Python — check what PyTorch and JAX support
curl -s https://pypi.org/pypi/torch/json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['info']['version']); [print(c) for c in d['info']['classifiers'] if 'Python :: 3.' in c]"
curl -s https://pypi.org/pypi/jax/json  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['info']['version']); [print(c) for c in d['info']['classifiers'] if 'Python :: 3.' in c]"
```

## 5. Update repo references in the Dockerfile

Change the `git clone` line(s) to point to the new repo:
```dockerfile
RUN ln=`grep -n "exec " /usr/local/bin/_entrypoint.sh | tail -1 | cut -f1 -d:`; \
    sed -i "${ln}igit clone --recurse-submodules https://github.com/research-software-collaborations/<NEW-REPO>" /usr/local/bin/_entrypoint.sh
```

## 6. Create the binder branch and push files

```bash
# Create branch from main
gh api repos/research-software-collaborations/<NEW-REPO>/git/refs \
  --method POST --field ref=refs/heads/binder \
  --field sha=$(gh api repos/research-software-collaborations/<NEW-REPO>/git/refs/heads/main | jq -r '.object.sha')

# Clone and push
gh repo clone research-software-collaborations/<NEW-REPO> myrepo -- --branch binder --depth 1
# ... add/edit files ...
git -C myrepo add binder/
git -C myrepo commit -m "Add merged binder config"
git -C myrepo push origin binder
```

## 7. Validation workflow

The `.github/workflows/validate-binder.yml` workflow does a conda solver dry-run and pip availability check on every push to `binder/environment.yml`. It also has a manual trigger (`workflow_dispatch`).

- The workflow file must exist on **main** for the manual trigger to appear in the Actions UI
- After adding it to `binder`, also copy it to `main`

Common solve failures and fixes:

| Error | Fix |
|---|---|
| `qastle` not found | Move `servicex` to pip |
| `jaxlib` uninstall error | Move `jax`, `optax`, `equinox`, `flax` to pip |
| Package not installable | Check if it's on PyPI and move to pip section |

## 8. Test suite

Tests live in `tests/` on `main`. Run with:
```bash
bash tests/run_tests.sh
```
The summary table shows PASS/FAIL and which packages detected a GPU.
