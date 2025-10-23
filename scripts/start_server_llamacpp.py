import os
import yaml
from fastapi import FastAPI
from llama_cpp import Llama
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class InferenceRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7

def load_config():
    with open("config/model_config.yaml", "r") as f:
        return yaml.safe_load(f)

def load_model():
    config = load_config()
    
    # GGUF model path - we'll download a quantized version
    model_path = "./models/codellama-13b-instruct.Q4_K_M.gguf"
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Downloading GGUF model from HuggingFace...")
        from huggingface_hub import hf_hub_download
        
        # Download Q4_K_M quantized model (good balance of quality/speed)
        model_path = hf_hub_download(
            repo_id="TheBloke/CodeLlama-13B-Instruct-GGUF",
            filename="codellama-13b-instruct.Q4_K_M.gguf",
            local_dir="./models",
            local_dir_use_symlinks=False,
        )
        print(f"Downloaded to: {model_path}")
    
    print(f"Loading model from {model_path} with GPU acceleration...")
    
    # Load model with GPU layers
    # n_gpu_layers=-1 means offload all layers to GPU
    # n_ctx is context window size
    model = Llama(
        model_path=model_path,
        n_gpu_layers=-1,  # Offload all layers to GPU
        n_ctx=4096,  # Context window
        n_batch=512,  # Batch size for prompt processing
        verbose=True,  # Show loading info
    )
    
    print("Model loaded successfully with GPU acceleration!")
    return model

# Load model at startup
model = load_model()

@app.post("/generate")
async def generate_text(request: InferenceRequest):
    output = model(
        request.prompt,
        max_tokens=request.max_new_tokens,
        temperature=request.temperature,
        stop=["</s>"],  # CodeLlama stop token
        echo=False,  # Don't repeat the prompt
    )
    
    generated_text = output["choices"][0]["text"]
    return {"generated_text": generated_text}

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}

if __name__ == "__main__":
    config = load_config()
    print(f"Starting server on {config['server']['host']}:{config['server']['port']}")
    uvicorn.run(
        app,
        host=config["server"]["host"],
        port=config["server"]["port"]
    )
