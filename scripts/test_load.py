import os, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
model_name = "codellama/CodeLlama-13B-Instruct"
hf_token = os.environ.get("HF_TOKEN")
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
max_memory = {"cuda:0":"11000MB","cuda:1":"11000MB","cuda:2":"11000MB","cpu":"470000MB"}
print("Starting model load (8-bit). This will download and map layers — watch RAM/GPU)")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    max_memory=max_memory,
    load_in_8bit=True,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    use_auth_token=hf_token
)
print("Model loaded/sharded; summary:")
print(model.device_map)