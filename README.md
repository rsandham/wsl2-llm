# Local LLM Setup with WSL2

This project provides a streamlined setup for running open-source Large Language Models (LLMs) locally using Windows Subsystem for Linux 2 (WSL2).

## Prerequisites

- Windows 10/11 with WSL2 installed
- Docker Desktop with WSL2 backend
- Python 3.8+
- Git

## Setup Instructions

1. **WSL2 Setup**
   ```bash
   # Enable WSL2
   wsl --set-default-version 2
   
   # Install Ubuntu (if not already installed)
   wsl --install -d Ubuntu
   ```

2. **Project Setup**
   ```bash
   # Clone this repository
   git clone <your-repo-url>
   cd wsl2-llm
   
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Model Setup**
   - Configure model settings in `config/model_config.yaml`
   - Run the model download script
   - Start the inference server

## Project Structure

```
wsl2-llm/
├── config/
│   └── model_config.yaml
├── scripts/
│   ├── setup_wsl.sh
│   ├── download_model.py
│   └── start_server.py
├── src/
│   ├── inference/
│   └── utils/
└── docker/
    └── Dockerfile
```

## Usage

1. Configure your model settings in `config/model_config.yaml`
2. Run the setup script: `./scripts/setup_wsl.sh`
3. Start the inference server: `python scripts/start_server.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.