#!/bin/bash

# Install systemd service for LLM server

echo "Installing LLM Server systemd service..."

# Copy service file
sudo cp llm-server.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service (start on boot)
echo "Enabling service..."
sudo systemctl enable llm-server

# Start service
echo "Starting service..."
sudo systemctl start llm-server

# Show status
echo ""
echo "Service status:"
sudo systemctl status llm-server --no-pager

echo ""
echo "✅ Installation complete!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status llm-server    # Check status"
echo "  sudo systemctl stop llm-server      # Stop service"
echo "  sudo systemctl restart llm-server   # Restart service"
echo "  sudo journalctl -u llm-server -f    # View logs"
echo "  tail -f /var/log/llm-server.log     # View application logs"
