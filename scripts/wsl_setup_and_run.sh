#!/usr/bin/env bash
set -euo pipefail

# Run from repository root inside WSL
echo "Working directory: $(pwd)"

# Create venv if missing and activate
if [ -d "venv" ]; then
  echo "Using existing venv"
else
  python3 -m venv venv
fi

# shellcheck source=/dev/null
source venv/bin/activate
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt || {
  echo "pip install failed. Check errors above. Exiting."; exit 1
}

# Ensure hf CLI is available
if command -v hf >/dev/null 2>&1; then
  echo "Using 'hf' CLI for authentication"
else
  python -m pip install huggingface_hub
fi

# Prompt for auth if HF_TOKEN not set
if [ -z "${HF_TOKEN:-}" ]; then
  echo "HF_TOKEN not set. Launching interactive login. When prompted, paste your Hugging Face token."
  if command -v hf >/dev/null 2>&1; then
    hf auth login || true
  else
    huggingface-cli login || true
  fi
else
  echo "HF_TOKEN environment variable is set; using it for downloads."
fi

# Download model
python scripts/download_model.py

# Start server in background with offload folder
OFFLOAD_FOLDER=./offload
export OFFLOAD_FOLDER
mkdir -p "$OFFLOAD_FOLDER"
nohup python scripts/start_server.py > server.log 2>&1 &
PID=$!
echo "$PID" > server.pid
sleep 1
if ps -p "$PID" >/dev/null 2>&1; then
  echo "Server started in background. PID=${PID}. Logs: server.log"
else
  echo "Server failed to start. Check server.log for errors."
  tail -n +1 server.log | sed -n '1,200p'
  exit 1
fi
