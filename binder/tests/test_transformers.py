import torch
import transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification

print(f"transformers version: {transformers.__version__}")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# load a tiny model (distilbert-base-uncased is ~250MB; use a config-only check
# to avoid downloading weights in a CI/test context)
from transformers import DistilBertConfig, DistilBertModel
config = DistilBertConfig(
    vocab_size=100, max_position_embeddings=16,
    n_heads=2, n_layers=2, dim=32, hidden_dim=64,
)
model = DistilBertModel(config).to(device)
model.eval()

tokenizer_input = torch.randint(0, 100, (1, 8)).to(device)
with torch.no_grad():
    out = model(input_ids=tokenizer_input)
print(f"transformers DistilBert (random config) OK, output shape: {out.last_hidden_state.shape}")

# peft: wrap with LoRA
from peft import get_peft_model, LoraConfig, TaskType
lora_config = LoraConfig(
    task_type=TaskType.FEATURE_EXTRACTION,
    r=2, lora_alpha=4, lora_dropout=0.1,
    target_modules=["q_lin"],
)
peft_model = get_peft_model(model, lora_config)
peft_model.print_trainable_parameters()
print("PASS: transformers + peft")
