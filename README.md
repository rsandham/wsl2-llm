# Local LLM Setup with WSL2

This project provides GPU-accelerated inference for CodeLlama-13B using llama.cpp in WSL2 (no PyTorch required!).

## Features

- ✅ **GPU Acceleration**: Uses llama.cpp with CUDA for fast inference
- ✅ **Multi-GPU Support**: Automatically distributes across available GPUs
- ✅ **4-bit Quantization**: Efficient Q4_K_M model (7.87GB)
- ✅ **REST API**: FastAPI server with `/generate` endpoint
- ✅ **Older GPU Support**: Works with compute capability 5.2+ (Pascal, Maxwell)

## Prerequisites

- Windows 10/11 with WSL2 installed
- NVIDIA GPU with CUDA support
- Python 3.11+
- CUDA Toolkit 12.6+ (installed automatically)

## Quick Start

### 1. Clone and Setup Virtual Environment
```bash
git clone https://github.com/rsandham/wsl2-llm.git
cd wsl2-llm
python3 -m venv venv311
source venv311/bin/activate
```

### 2. Install Dependencies
```bash
# Install build tools (one-time setup)
sudo apt update
sudo apt install -y build-essential gcc g++ cmake

# Install CUDA Toolkit (one-time setup)
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-6

# Install Python packages with CUDA support
export PATH=/usr/local/cuda-12.6/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
export CUDACXX=/usr/local/cuda-12.6/bin/nvcc

pip install -r requirements.txt
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### 3. Start the Server
```bash
# Set CUDA environment
export PATH=/usr/local/cuda-12.6/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH

# Start server (downloads model on first run)
python3 scripts/start_server_llamacpp.py
```

The server will:
- Download CodeLlama-13B-Instruct GGUF model (~7.87GB) on first run
- Load model across all available GPUs
- Start REST API on `http://0.0.0.0:8000`

## Project Structure

```
wsl2-llm/
├── config/
│   └── model_config.yaml          # Model configuration
├── scripts/
│   ├── start_server_llamacpp.py   # Main server (llama.cpp)
│   ├── start_server.py            # Legacy PyTorch server
│   ├── download_model.py          # Model downloader
│   └── test_load.py               # Test script
├── models/                        # Downloaded models (auto-created)
├── test_server.sh                 # API test script
└── requirements.txt               # Python dependencies
```

## Usage

### Testing the API

Run the test script:
```bash
./test_server.sh
```

Or use curl directly:

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Generate Code:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def fibonacci(n):",
    "max_new_tokens": 100,
    "temperature": 0.7
  }'
```

### Monitor GPU Usage

```bash
watch -n 1 nvidia-smi
```

## Configuration

Edit `config/model_config.yaml` to adjust:
- Server host/port
- Context window size
- GPU memory allocation

## Performance

With 3x NVIDIA GPUs and Q4_K_M quantization:
- **Model Loading**: ~30 seconds
- **Inference Speed**: ~20-40 tokens/second
- **VRAM Usage**: ~7.5GB total across GPUs
- **Context Window**: 4096 tokens (configurable up to 16384)

## Troubleshooting

**CUDA not found:**
```bash
export PATH=/usr/local/cuda-12.6/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
```

**GPU not detected:**
```bash
nvidia-smi  # Should show your GPUs
```

**Model download fails:**
- Check internet connection
- Verify HuggingFace access (some models need authentication)

## Contributing

Contributions welcome! Please submit a Pull Request.

## License

MIT License - see LICENSE file for details.