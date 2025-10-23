import os
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login as hf_login


def load_config():
    with open("config/model_config.yaml", "r") as f:
        return yaml.safe_load(f)

def download_model():
    config = load_config()
    model_name = config["model"]["name"]
    model_path = config["model"]["path"]
    
    print(f"Downloading model {model_name}...")

    # Try to get token from environment or HF token file
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token and os.path.exists(os.path.expanduser("~/.huggingface/token")):
        with open(os.path.expanduser("~/.huggingface/token"), "r") as f:
            hf_token = f.read().strip()
    
    if hf_token:
        print("Using HF token from environment or token file.")
        # Login with the token
        hf_login(token=hf_token)
    else:
        print("No HF token found. If the model is gated you'll need to set HF_TOKEN or run `huggingface-cli login`.")
    
    # Create model directory if it doesn't exist
    os.makedirs(model_path, exist_ok=True)
    
    # Download model and tokenizer
    # Pass token when available to support gated models
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        use_auth_token=hf_token
    )
    
    # Save model and tokenizer
    model.save_pretrained(os.path.join(model_path, model_name))
    tokenizer.save_pretrained(os.path.join(model_path, model_name))
    
    print(f"Model downloaded and saved to {model_path}/{model_name}")

if __name__ == "__main__":
    download_model()