import os
import yaml
from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
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
    model_name = config["model"]["name"]
    hf_token = os.environ.get("HF_TOKEN")

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)

    max_memory = config.get("optimization", {}).get("max_memory", {
        "cuda:0": "11000MB",
        "cuda:1": "11000MB",
        "cuda:2": "11000MB",
        "cpu":    "470000MB",
    })

    # Use BitsAndBytesConfig for 8-bit quantization (proper method)
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        bnb_8bit_compute_dtype=torch.float16,
    )

    print(f"Loading model {model_name} with 8-bit quantization...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        max_memory=max_memory,
        offload_folder=config.get("optimization", {}).get("offload_folder", "./offload"),
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        token=hf_token,
    )
    
    print("Model loaded successfully!")
    print(f"Device map: {model.hf_device_map}")
    return model, tokenizer

model, tokenizer = load_model()

@app.post("/generate")
async def generate_text(request: InferenceRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt")
    # Move inputs to the model's device
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    outputs = model.generate(
        inputs["input_ids"],
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        do_sample=True,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_text": response}

if __name__ == "__main__":
    config = load_config()
    uvicorn.run(
        app,
        host=config["server"]["host"],
        port=config["server"]["port"]
    )