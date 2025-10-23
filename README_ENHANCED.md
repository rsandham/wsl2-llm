# WSL2 LLM Inference Server

Production-ready GPU-accelerated LLM inference server using llama.cpp and CodeLlama-13B.

## 🌟 Features

- **🚀 GPU Acceleration**: Multi-GPU support with automatic layer distribution
- **⚡ Fast Inference**: GGUF Q4_K_M quantization for optimal speed/quality balance
- **🔒 API Security**: Optional API key authentication middleware
- **🌐 Interactive Web UI**: Beautiful web interface with real-time stats
- **📡 Multiple Endpoints**:
  - `/generate` - General text generation
  - `/complete` - Code completion
  - `/chat` - Conversational interface with message history
  - `/batch` - Batch processing for multiple prompts
  - `/health` - Health check and status
- **🔧 SystemD Service**: Auto-start on boot with systemd integration
- **📊 Performance Metrics**: Real-time token counts, generation speed
- **💻 No PyTorch Required**: Uses llama.cpp for broader GPU compatibility
- **🎯 Older GPU Support**: Works with compute capability 5.2+ (Maxwell, Pascal)

## 📋 Prerequisites

- Windows 10/11 with WSL2 installed
- NVIDIA GPU with CUDA support (compute capability 5.2+)
- Python 3.11+
- CUDA Toolkit 12.6+
- 8GB+ VRAM recommended

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/rsandham/wsl2-llm.git
cd wsl2-llm
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv311
source venv311/bin/activate
```

### 3. Install System Dependencies
```bash
# Install build tools (one-time)
sudo apt update
sudo apt install -y build-essential gcc g++ cmake

# Install CUDA Toolkit 12.6 (one-time)
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-6
```

### 4. Install Python Dependencies
```bash
# Set CUDA environment variables
export PATH=/usr/local/cuda-12.6/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
export CUDACXX=/usr/local/cuda-12.6/bin/nvcc

# Install base dependencies
pip install -r requirements.txt

# Build llama-cpp-python with CUDA support
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### 5. Start the Server
```bash
# Option A: Run directly
python scripts/start_server_enhanced.py

# Option B: Install as systemd service (runs on boot)
./install_service.sh
```

The model will be automatically downloaded on first run (~7.87GB).

## 🔐 API Authentication

To enable API key authentication:

```bash
# Set API key environment variable
export LLM_API_KEY="your-secret-key-here"

# Add to systemd service (edit llm-server.service):
Environment="LLM_API_KEY=your-secret-key-here"

# Include in API requests:
curl -H "X-API-Key: your-secret-key-here" http://localhost:8000/generate
```

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Text
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def fibonacci(n):\n    \"\"\"Calculate fibonacci\"\"\"",
    "max_new_tokens": 200,
    "temperature": 0.7
  }'
```

### Code Completion
```bash
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def quicksort(arr):\n    \"\"\"Sort array\"\"\"",
    "max_new_tokens": 150,
    "temperature": 0.3
  }'
```

### Chat Interface
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful coding assistant."},
      {"role": "user", "content": "How do I reverse a string in Python?"}
    ],
    "max_new_tokens": 200,
    "temperature": 0.7
  }'
```

### Batch Processing
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "def factorial(n):",
      "class Stack:",
      "def merge_sort(arr):"
    ],
    "max_new_tokens": 100,
    "temperature": 0.3
  }'
```

## 🌐 Web Interface

Open your browser to `http://localhost:8000/ui` for the interactive web interface.

Features:
- 📝 Text generation with customizable parameters
- 💻 Code completion
- 💬 Chat interface with message history
- 📦 Batch processing
- 📊 Real-time performance metrics
- 🎨 Beautiful, responsive design

## 🔧 SystemD Service Management

### Install Service
```bash
./install_service.sh
```

### Service Commands
```bash
# Check status
sudo systemctl status llm-server

# Start/stop/restart
sudo systemctl start llm-server
sudo systemctl stop llm-server
sudo systemctl restart llm-server

# Enable/disable auto-start
sudo systemctl enable llm-server
sudo systemctl disable llm-server

# View logs
sudo journalctl -u llm-server -f
tail -f /var/log/llm-server.log
```

## 🧪 Testing

Run comprehensive tests:
```bash
./test_server_enhanced.sh
```

This tests all endpoints: health, generate, complete, chat, batch, and web UI.

## ⚙️ Configuration

Edit `config/model_config.yaml`:
```yaml
server:
  host: 0.0.0.0
  port: 8000

optimization:
  max_batch_size: 8
  max_input_length: 4096
  max_new_tokens: 512
```

## 🐛 Troubleshooting

### GPU Not Detected
```bash
# Check GPU availability
nvidia-smi

# Verify CUDA installation
nvcc --version

# Check llama-cpp-python CUDA support
python -c "from llama_cpp import Llama; print('CUDA available')"
```

### Out of Memory
- Reduce `n_ctx` in `start_server_enhanced.py` (default: 4096)
- Reduce `n_batch` (default: 512)
- Use smaller model or different quantization

### Slow Generation
- Check GPU usage: `nvidia-smi`
- Verify all layers are on GPU (check startup logs for "offloaded 41/41 layers")
- Reduce `max_new_tokens` for faster responses

### CUDA Library Not Found
```bash
# Add CUDA to library path permanently
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Service Won't Start
```bash
# Check service logs
sudo journalctl -u llm-server -n 50 --no-pager

# Verify permissions
ls -la /home/rsandham/projects/wsl2-llm/

# Test manually first
source venv311/bin/activate
python scripts/start_server_enhanced.py
```

## 📊 Performance

On 3x NVIDIA GPUs (2x TITAN X Pascal, 1x GTX TITAN X):
- Model loading: ~30 seconds
- Inference speed: 20-40 tokens/second
- VRAM usage: ~7.5GB total across GPUs
- Layer distribution: Automatic across all GPUs

## 🛠️ Architecture

```
┌─────────────────────────────────────────┐
│          FastAPI Server                 │
│  - Authentication Middleware            │
│  - Multiple Endpoints                   │
│  - Web UI (Static HTML/CSS/JS)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       llama-cpp-python                  │
│  - GGUF Model Loading                   │
│  - GPU Layer Offloading                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          CUDA Runtime                   │
│  GPU0: Layers 0-13                      │
│  GPU1: Layers 14-27                     │
│  GPU2: Layers 28-40                     │
└─────────────────────────────────────────┘
```

## 📦 Project Structure

```
wsl2-llm/
├── config/
│   └── model_config.yaml          # Server configuration
├── models/
│   └── codellama-13b-instruct.Q4_K_M.gguf  # GGUF model
├── scripts/
│   ├── start_server_enhanced.py   # Main production server
│   ├── start_server_llamacpp.py   # Simple server (legacy)
│   └── download_model.py          # Model downloader
├── static/                        # Web UI assets
│   ├── index.html                 # Main HTML page
│   ├── css/
│   │   └── style.css              # Stylesheet
│   └── js/
│       └── app.js                 # Client-side logic
├── llm-server.service             # SystemD service file
├── install_service.sh             # Service installer
├── test_server_enhanced.sh        # Comprehensive tests
├── requirements.txt               # Python dependencies
└── README.md                      # Documentation
```

## 🎨 Frontend Architecture

The web UI follows modern best practices:

- **Separation of Concerns**: HTML, CSS, and JavaScript in separate files
- **Component-Based CSS**: Organized by component type
- **Modern JavaScript**: ES6+ with async/await
- **No Dependencies**: Pure vanilla JS, no frameworks needed
- **Responsive Design**: Works on desktop and tablet devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [CodeLlama](https://github.com/facebookresearch/codellama) - Meta's code model
- [TheBloke](https://huggingface.co/TheBloke) - GGUF model conversions

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check troubleshooting section above
- Review llama.cpp documentation

---

**Built with ❤️ for GPU-accelerated AI inference**
