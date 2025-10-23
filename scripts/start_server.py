import os
import yaml
from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import uvicorn
from pydantic import BaseModel
from huggingface_hub import hf_hub_download

app = FastAPI()

class InferenceRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7

def load_config():
    with open("config/model_config.yaml", "r") as f:
        return yaml.safe_load(f)

def load_model():
    config = load_config()  # your existing loader
    model_name = config["model"]["name"]
    hf_token = os.environ.get("HF_TOKEN")

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)

    max_memory = config.get("optimization", {}).get("max_memory", {
        "cuda:0": "11000MB",
        "cuda:1": "11000MB",
        "cuda:2": "11000MB",
        "cpu":    "470000MB",
    })

    # For stable start: use 8-bit first (bitsandbytes), then experiment with 4-bit
    # For 4-bit you may need specific bitsandbytes settings and recent transformers
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        max_memory=max_memory,
        offload_folder=config.get("optimization", {}).get("offload_folder", "./offload"),
        load_in_8bit=True,            # start with 8-bit; switch to 4-bit if you set up flags
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        use_auth_token=hf_token,
    )

    # For 4-bit via bitsandbytes (optional, more advanced):
    # model = AutoModelForCausalLM.from_pretrained(
    #     model_name,
    #     device_map="auto",
    #     max_memory=max_memory,
    #     offload_folder="./offload",
    #     load_in_4bit=True,
    #     bnb_4bit_use_double_quant=True,
    #     bnb_4bit_quant_type='nf4',
    #     torch_dtype=torch.float16,
    #     low_cpu_mem_usage=True,
    #     use_auth_token=hf_token,
    # )
    return model, tokenizer

model, tokenizer = load_model()

@app.post("/generate")
async def generate_text(request: InferenceRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt")
    
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