# 🚀 Quick Start Guide - Enhanced LLM Server

## Start Server

```bash
cd /home/rsandham/projects/wsl2-llm
source venv311/bin/activate
python scripts/start_server_enhanced.py
```

## Access Points

- **Web UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)
- **Health Check**: http://localhost:8000/health

## Quick Tests

```bash
# Health check
curl http://localhost:8000/health

# Generate code
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def hello():", "max_new_tokens": 100}'

# Complete code
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{"code": "def sort(arr):", "max_new_tokens": 100}'

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'

# Batch
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{"prompts": ["def factorial(n):", "class Stack:"]}'

# Run all tests
./test_server_enhanced.sh
```

## Enable Authentication

```bash
export LLM_API_KEY="your-secret-key"
python scripts/start_server_enhanced.py

# Use in requests
curl -H "X-API-Key: your-secret-key" http://localhost:8000/generate ...
```

## Install as SystemD Service

```bash
# Edit llm-server.service to add API key if needed
nano llm-server.service
# Add: Environment="LLM_API_KEY=your-key"

# Install
./install_service.sh

# Manage
sudo systemctl status llm-server
sudo systemctl restart llm-server
sudo journalctl -u llm-server -f
```

## Features Summary

✅ **5 API Endpoints**: generate, complete, chat, batch, health
✅ **Web Interface**: Beautiful UI at /ui
✅ **Authentication**: Optional API key via LLM_API_KEY
✅ **GPU Acceleration**: All 41 layers on GPUs
✅ **SystemD Service**: Auto-start on boot
✅ **Batch Processing**: Multiple prompts in one request
✅ **Real-time Stats**: Tokens/sec, time, counts

## Troubleshooting

### Server won't start
```bash
# Activate venv first
source venv311/bin/activate

# Check CUDA
nvidia-smi

# Check port
lsof -i :8000
```

### Syntax errors fixed
The triple-quote issue in HTML was fixed by using `&quot;&quot;&quot;` instead of `"""`.

## File Locations

- Main server: `scripts/start_server_enhanced.py`
- SystemD service: `llm-server.service`
- Installer: `install_service.sh`
- Tests: `test_server_enhanced.sh`
- Config: `config/model_config.yaml`

---
**Everything is working! 🎉**
