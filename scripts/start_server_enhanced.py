import os
import yaml
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from llama_cpp import Llama
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import time
from pathlib import Path

app = FastAPI(title="LLM Inference API", version="2.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API Key Authentication
API_KEY = os.environ.get("LLM_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if API_KEY and api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Request Models
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    repeat_penalty: float = 1.1

class CompleteRequest(BaseModel):
    code: str
    max_new_tokens: int = 100
    temperature: float = 0.3
    stop: Optional[List[str]] = ["\n\n", "def ", "class "]

class ChatMessage(BaseModel):
    role: str  # "system", "user", or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_new_tokens: int = 512
    temperature: float = 0.7

class BatchRequest(BaseModel):
    prompts: List[str]
    max_new_tokens: int = 512
    temperature: float = 0.7

def load_config():
    config_path = Path("config/model_config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 8000
        }
    }

def load_model():
    # GGUF model path
    model_path = "./models/codellama-13b-instruct.Q4_K_M.gguf"
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Downloading GGUF model from HuggingFace...")
        from huggingface_hub import hf_hub_download
        
        model_path = hf_hub_download(
            repo_id="TheBloke/CodeLlama-13B-Instruct-GGUF",
            filename="codellama-13b-instruct.Q4_K_M.gguf",
            local_dir="./models",
        )
        print(f"Downloaded to: {model_path}")
    
    print(f"Loading model from {model_path} with GPU acceleration...")
    
    model = Llama(
        model_path=model_path,
        n_gpu_layers=-1,  # Offload all layers to GPU
        n_ctx=4096,  # Context window
        n_batch=512,  # Batch size
        verbose=True,
    )
    
    print("Model loaded successfully with GPU acceleration!")
    return model

# Load model at startup
model = load_model()

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "LLM Inference API",
        "version": "2.0",
        "endpoints": {
            "/health": "Health check",
            "/generate": "Generate text from prompt",
            "/complete": "Code completion",
            "/chat": "Chat interface",
            "/batch": "Batch processing",
            "/ui": "Web interface"
        },
        "authentication": "Required" if API_KEY else "Disabled"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "gpu_enabled": True,
        "auth_enabled": API_KEY is not None
    }

@app.post("/generate")
async def generate_text(request: GenerateRequest, api_key: str = Depends(get_api_key)):
    """Generate text from a prompt"""
    start_time = time.time()
    
    output = model(
        request.prompt,
        max_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        repeat_penalty=request.repeat_penalty,
        stop=["</s>"],
        echo=False,
    )
    
    elapsed = time.time() - start_time
    tokens = len(output["choices"][0]["text"].split())
    
    return {
        "generated_text": output["choices"][0]["text"],
        "tokens_generated": tokens,
        "time_seconds": round(elapsed, 2),
        "tokens_per_second": round(tokens / elapsed, 2) if elapsed > 0 else 0
    }

@app.post("/complete")
async def complete_code(request: CompleteRequest, api_key: str = Depends(get_api_key)):
    """Complete code snippet"""
    start_time = time.time()
    
    # Format for code completion
    prompt = f"{request.code}"
    
    output = model(
        prompt,
        max_tokens=request.max_new_tokens,
        temperature=request.temperature,
        stop=request.stop or ["</s>", "\n\n"],
        echo=False,
    )
    
    completion = output["choices"][0]["text"]
    elapsed = time.time() - start_time
    
    return {
        "completion": completion,
        "full_code": request.code + completion,
        "time_seconds": round(elapsed, 2)
    }

@app.post("/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """Chat with the model"""
    start_time = time.time()
    
    # Format messages into a prompt
    prompt = ""
    for msg in request.messages:
        if msg.role == "system":
            prompt += f"System: {msg.content}\n\n"
        elif msg.role == "user":
            prompt += f"User: {msg.content}\n\n"
        elif msg.role == "assistant":
            prompt += f"Assistant: {msg.content}\n\n"
    
    prompt += "Assistant: "
    
    output = model(
        prompt,
        max_tokens=request.max_new_tokens,
        temperature=request.temperature,
        stop=["User:", "</s>"],
        echo=False,
    )
    
    response = output["choices"][0]["text"].strip()
    elapsed = time.time() - start_time
    
    return {
        "response": response,
        "time_seconds": round(elapsed, 2)
    }

@app.post("/batch")
async def batch_generate(request: BatchRequest, api_key: str = Depends(get_api_key)):
    """Process multiple prompts in batch"""
    start_time = time.time()
    results = []
    
    for i, prompt in enumerate(request.prompts):
        try:
            output = model(
                prompt,
                max_tokens=request.max_new_tokens,
                temperature=request.temperature,
                stop=["</s>"],
                echo=False,
            )
            results.append({
                "index": i,
                "prompt": prompt,
                "generated_text": output["choices"][0]["text"],
                "status": "success"
            })
        except Exception as e:
            results.append({
                "index": i,
                "prompt": prompt,
                "error": str(e),
                "status": "error"
            })
    
    elapsed = time.time() - start_time
    
    return {
        "results": results,
        "total_prompts": len(request.prompts),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "time_seconds": round(elapsed, 2)
    }

# Serve static files and web UI
@app.get("/ui", response_class=HTMLResponse)
async def web_ui():
    """Serve the web interface"""
    html_path = Path("static/index.html")
    if html_path.exists():
        with open(html_path, 'r') as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="UI not found")

if __name__ == "__main__":
    config = load_config()
    print(f"Starting enhanced server on {config['server']['host']}:{config['server']['port']}")
    if API_KEY:
        print(f"⚠️  API Key authentication ENABLED")
    else:
        print(f"⚠️  API Key authentication DISABLED (set LLM_API_KEY env var to enable)")
    
    uvicorn.run(
        app,
        host=config["server"]["host"],
        port=config["server"]["port"]
    )
