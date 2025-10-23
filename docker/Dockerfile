FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY src/ ./src/

# Create models directory
RUN mkdir -p models

# Expose the port the server runs on
EXPOSE 8000

# Start the inference server
CMD ["python", "scripts/start_server.py"]