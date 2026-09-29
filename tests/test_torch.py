import torch
import torchvision
import torch_geometric

print(f"PyTorch version: {torch.__version__}")
print(f"Torchvision version: {torchvision.__version__}")
print(f"PyG version: {torch_geometric.__version__}")

if torch.cuda.is_available():
    n = torch.cuda.device_count()
    print(f"CUDA available: {n} GPU(s)")
    for i in range(n):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    device = torch.device("cuda")
else:
    print("CUDA not available — running on CPU")
    device = torch.device("cpu")

# basic tensor op
x = torch.randn(256, 256, device=device)
y = torch.randn(256, 256, device=device)
z = x @ y
print(f"Matrix multiply OK, result shape: {z.shape}, device: {z.device}")

# minimal PyG graph
from torch_geometric.data import Data
edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
data = Data(x=torch.randn(2, 4), edge_index=edge_index)
print(f"PyG Data OK: {data}")

print("PASS: torch")
