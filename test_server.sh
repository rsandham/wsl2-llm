#!/bin/bash

echo "Testing wsl2-llm server..."
echo ""

# Health check
echo "1. Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Code generation test
echo "2. Code Generation Test:"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def fibonacci(n):\n    \"\"\"Calculate fibonacci number recursively\"\"\"",
    "max_new_tokens": 150,
    "temperature": 0.3
  }' | python3 -m json.tool
echo ""
echo ""

# Another test - implement quicksort
echo "3. Quicksort Implementation Test:"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def quicksort(arr):\n    \"\"\"Sort array using quicksort algorithm\"\"\"",
    "max_new_tokens": 200,
    "temperature": 0.2
  }' | python3 -m json.tool

echo ""
echo "Tests complete!"
