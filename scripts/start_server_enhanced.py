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
    """Simple web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LLM Inference UI</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #e0e0e0;
            }
            .tab {
                padding: 15px 30px;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 16px;
                color: #666;
                transition: all 0.3s;
                border-bottom: 3px solid transparent;
            }
            .tab.active {
                color: #667eea;
                border-bottom-color: #667eea;
                font-weight: bold;
            }
            .tab:hover {
                color: #667eea;
                background: #f8f8f8;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .input-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            textarea, input[type="text"], input[type="number"] {
                width: 100%;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
                transition: border 0.3s;
            }
            textarea:focus, input:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                min-height: 200px;
                resize: vertical;
            }
            .params {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .output {
                background: #f8f9fa;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                min-height: 100px;
                max-height: 500px;
                overflow-y: auto;
            }
            .loading {
                text-align: center;
                color: #667eea;
                font-weight: bold;
                padding: 20px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .stats {
                display: flex;
                gap: 20px;
                margin-top: 10px;
                font-size: 14px;
                color: #666;
            }
            .stat {
                background: #f0f0f0;
                padding: 8px 15px;
                border-radius: 5px;
            }
            .chat-messages {
                max-height: 400px;
                overflow-y: auto;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                background: #f8f9fa;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 8px;
            }
            .message.user {
                background: #667eea;
                color: white;
                margin-left: 20%;
            }
            .message.assistant {
                background: #e0e0e0;
                margin-right: 20%;
            }
            .message-role {
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 12px;
                text-transform: uppercase;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 LLM Inference Server</h1>
            <p class="subtitle">GPU-Accelerated CodeLlama-13B</p>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab('generate')">Generate</button>
                <button class="tab" onclick="switchTab('complete')">Complete Code</button>
                <button class="tab" onclick="switchTab('chat')">Chat</button>
                <button class="tab" onclick="switchTab('batch')">Batch</button>
            </div>
            
            <!-- Generate Tab -->
            <div id="generate" class="tab-content active">
                <div class="input-group">
                    <label>Prompt:</label>
                    <textarea id="gen-prompt" placeholder="Enter your prompt here...">def fibonacci(n):
    """Calculate fibonacci number"""</textarea>
                </div>
                <div class="params">
                    <div class="input-group">
                        <label>Max Tokens:</label>
                        <input type="number" id="gen-tokens" value="512" min="1" max="2048">
                    </div>
                    <div class="input-group">
                        <label>Temperature:</label>
                        <input type="number" id="gen-temp" value="0.7" step="0.1" min="0" max="2">
                    </div>
                    <div class="input-group">
                        <label>API Key (optional):</label>
                        <input type="text" id="api-key" placeholder="Enter API key if required">
                    </div>
                </div>
                <button onclick="generate()">Generate</button>
                <div id="gen-output" class="output"></div>
                <div id="gen-stats" class="stats"></div>
            </div>
            
            <!-- Complete Tab -->
            <div id="complete" class="tab-content">
                <div class="input-group">
                    <label>Code to Complete:</label>
                    <textarea id="code-input" placeholder="Enter code to complete...">def quicksort(arr):
    """Sort array using quicksort"""</textarea>
                </div>
                <div class="params">
                    <div class="input-group">
                        <label>Max Tokens:</label>
                        <input type="number" id="complete-tokens" value="150" min="1" max="1000">
                    </div>
                    <div class="input-group">
                        <label>Temperature:</label>
                        <input type="number" id="complete-temp" value="0.3" step="0.1" min="0" max="1">
                    </div>
                </div>
                <button onclick="complete()">Complete Code</button>
                <div id="complete-output" class="output"></div>
            </div>
            
            <!-- Chat Tab -->
            <div id="chat" class="tab-content">
                <div class="chat-messages" id="chat-messages"></div>
                <div class="input-group">
                    <label>Your Message:</label>
                    <textarea id="chat-input" placeholder="Type your message..." rows="3"></textarea>
                </div>
                <button onclick="sendChat()">Send Message</button>
            </div>
            
            <!-- Batch Tab -->
            <div id="batch" class="tab-content">
                <div class="input-group">
                    <label>Prompts (one per line):</label>
                    <textarea id="batch-prompts" placeholder="Enter multiple prompts, one per line...">def hello_world():
def fibonacci(n):
class Calculator:</textarea>
                </div>
                <div class="params">
                    <div class="input-group">
                        <label>Max Tokens per Prompt:</label>
                        <input type="number" id="batch-tokens" value="200" min="1" max="1000">
                    </div>
                </div>
                <button onclick="batchProcess()">Process Batch</button>
                <div id="batch-output" class="output"></div>
            </div>
        </div>
        
        <script>
            let chatHistory = [];
            
            function switchTab(tabName) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById(tabName).classList.add('active');
            }
            
            function getHeaders() {
                const apiKey = document.getElementById('api-key').value;
                const headers = {'Content-Type': 'application/json'};
                if (apiKey) headers['X-API-Key'] = apiKey;
                return headers;
            }
            
            async function generate() {
                const output = document.getElementById('gen-output');
                const stats = document.getElementById('gen-stats');
                output.innerHTML = '<div class="loading"><div class="spinner"></div>Generating...</div>';
                stats.innerHTML = '';
                
                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        headers: getHeaders(),
                        body: JSON.stringify({
                            prompt: document.getElementById('gen-prompt').value,
                            max_new_tokens: parseInt(document.getElementById('gen-tokens').value),
                            temperature: parseFloat(document.getElementById('gen-temp').value)
                        })
                    });
                    
                    const data = await response.json();
                    if (response.ok) {
                        output.textContent = data.generated_text;
                        stats.innerHTML = `
                            <div class="stat">⏱️ ${data.time_seconds}s</div>
                            <div class="stat">📝 ${data.tokens_generated} tokens</div>
                            <div class="stat">⚡ ${data.tokens_per_second} tok/s</div>
                        `;
                    } else {
                        output.textContent = 'Error: ' + (data.detail || 'Unknown error');
                    }
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            async function complete() {
                const output = document.getElementById('complete-output');
                output.innerHTML = '<div class="loading"><div class="spinner"></div>Completing...</div>';
                
                try {
                    const response = await fetch('/complete', {
                        method: 'POST',
                        headers: getHeaders(),
                        body: JSON.stringify({
                            code: document.getElementById('code-input').value,
                            max_new_tokens: parseInt(document.getElementById('complete-tokens').value),
                            temperature: parseFloat(document.getElementById('complete-temp').value)
                        })
                    });
                    
                    const data = await response.json();
                    if (response.ok) {
                        output.textContent = data.full_code;
                    } else {
                        output.textContent = 'Error: ' + (data.detail || 'Unknown error');
                    }
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            async function sendChat() {
                const input = document.getElementById('chat-input');
                const messages = document.getElementById('chat-messages');
                const userMessage = input.value.trim();
                
                if (!userMessage) return;
                
                // Add user message to UI
                chatHistory.push({role: 'user', content: userMessage});
                updateChatUI();
                input.value = '';
                
                // Show loading
                messages.innerHTML += '<div class="loading"><div class="spinner"></div>Thinking...</div>';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: getHeaders(),
                        body: JSON.stringify({
                            messages: chatHistory,
                            max_new_tokens: 512,
                            temperature: 0.7
                        })
                    });
                    
                    const data = await response.json();
                    if (response.ok) {
                        chatHistory.push({role: 'assistant', content: data.response});
                        updateChatUI();
                    } else {
                        messages.innerHTML += `<div class="message">Error: ${data.detail || 'Unknown error'}</div>`;
                    }
                } catch (error) {
                    messages.innerHTML += `<div class="message">Error: ${error.message}</div>`;
                }
            }
            
            function updateChatUI() {
                const messages = document.getElementById('chat-messages');
                messages.innerHTML = chatHistory.map(msg => `
                    <div class="message ${msg.role}">
                        <div class="message-role">${msg.role}</div>
                        <div>${msg.content}</div>
                    </div>
                `).join('');
                messages.scrollTop = messages.scrollHeight;
            }
            
            async function batchProcess() {
                const output = document.getElementById('batch-output');
                const prompts = document.getElementById('batch-prompts').value
                    .split('\n')
                    .filter(p => p.trim());
                
                if (prompts.length === 0) {
                    output.textContent = 'Please enter at least one prompt';
                    return;
                }
                
                output.innerHTML = '<div class="loading"><div class="spinner"></div>Processing batch...</div>';
                
                try {
                    const response = await fetch('/batch', {
                        method: 'POST',
                        headers: getHeaders(),
                        body: JSON.stringify({
                            prompts: prompts,
                            max_new_tokens: parseInt(document.getElementById('batch-tokens').value),
                            temperature: 0.7
                        })
                    });
                    
                    const data = await response.json();
                    if (response.ok) {
                        let result = `✅ Processed ${data.successful}/${data.total_prompts} prompts in ${data.time_seconds}s\n\n`;
                        data.results.forEach((r, i) => {
                            result += `\n━━━ Prompt ${i + 1} ━━━\n`;
                            result += `${r.prompt}\n\n`;
                            result += `Generated:\n${r.generated_text}\n`;
                        });
                        output.textContent = result;
                    } else {
                        output.textContent = 'Error: ' + (data.detail || 'Unknown error');
                    }
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            // Enter key support for chat
            document.getElementById('chat-input').addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChat();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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
