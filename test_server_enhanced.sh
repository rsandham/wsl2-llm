#!/bin/bash

# Comprehensive test script for enhanced LLM server

BASE_URL="http://localhost:8000"
API_KEY="${LLM_API_KEY:-}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Header for API key if set
if [ -n "$API_KEY" ]; then
    AUTH_HEADER="-H \"X-API-Key: $API_KEY\""
    echo -e "${YELLOW}Using API Key authentication${NC}"
else
    AUTH_HEADER=""
    echo -e "${YELLOW}No API Key set (authentication disabled)${NC}"
fi

echo "================================"
echo "Testing LLM Server Endpoints"
echo "================================"
echo ""

# Test 1: Root endpoint
echo -e "${YELLOW}Test 1: Root Endpoint${NC}"
curl -s "$BASE_URL/" | jq '.'
echo ""

# Test 2: Health Check
echo -e "${YELLOW}Test 2: Health Check${NC}"
curl -s "$BASE_URL/health" | jq '.'
echo ""

# Test 3: Generate Text
echo -e "${YELLOW}Test 3: Generate Text (Fibonacci)${NC}"
if [ -n "$API_KEY" ]; then
    response=$(curl -s -X POST "$BASE_URL/generate" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{
            "prompt": "def fibonacci(n):\n    \"\"\"Calculate fibonacci number recursively\"\"\"",
            "max_new_tokens": 200,
            "temperature": 0.3
        }')
else
    response=$(curl -s -X POST "$BASE_URL/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "prompt": "def fibonacci(n):\n    \"\"\"Calculate fibonacci number recursively\"\"\"",
            "max_new_tokens": 200,
            "temperature": 0.3
        }')
fi
echo "$response" | jq '.'
echo ""

# Test 4: Code Completion
echo -e "${YELLOW}Test 4: Code Completion${NC}"
if [ -n "$API_KEY" ]; then
    response=$(curl -s -X POST "$BASE_URL/complete" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{
            "code": "def binary_search(arr, target):\n    \"\"\"Binary search implementation\"\"\"",
            "max_new_tokens": 150,
            "temperature": 0.2
        }')
else
    response=$(curl -s -X POST "$BASE_URL/complete" \
        -H "Content-Type: application/json" \
        -d '{
            "code": "def binary_search(arr, target):\n    \"\"\"Binary search implementation\"\"\"",
            "max_new_tokens": 150,
            "temperature": 0.2
        }')
fi
echo "$response" | jq '.'
echo ""

# Test 5: Chat Interface
echo -e "${YELLOW}Test 5: Chat Interface${NC}"
if [ -n "$API_KEY" ]; then
    response=$(curl -s -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "How do I reverse a string in Python?"}
            ],
            "max_new_tokens": 200,
            "temperature": 0.7
        }')
else
    response=$(curl -s -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d '{
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "How do I reverse a string in Python?"}
            ],
            "max_new_tokens": 200,
            "temperature": 0.7
        }')
fi
echo "$response" | jq '.'
echo ""

# Test 6: Batch Processing
echo -e "${YELLOW}Test 6: Batch Processing${NC}"
if [ -n "$API_KEY" ]; then
    response=$(curl -s -X POST "$BASE_URL/batch" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{
            "prompts": [
                "def factorial(n):",
                "class Stack:",
                "def merge_sort(arr):"
            ],
            "max_new_tokens": 100,
            "temperature": 0.3
        }')
else
    response=$(curl -s -X POST "$BASE_URL/batch" \
        -H "Content-Type: application/json" \
        -d '{
            "prompts": [
                "def factorial(n):",
                "class Stack:",
                "def merge_sort(arr):"
            ],
            "max_new_tokens": 100,
            "temperature": 0.3
        }')
fi
echo "$response" | jq '.'
echo ""

# Test 7: Web UI Access
echo -e "${YELLOW}Test 7: Web UI Access${NC}"
ui_status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/ui")
if [ "$ui_status" == "200" ]; then
    echo -e "${GREEN}✓ Web UI is accessible at $BASE_URL/ui${NC}"
else
    echo -e "${RED}✗ Web UI returned status $ui_status${NC}"
fi
echo ""

echo "================================"
echo -e "${GREEN}All tests completed!${NC}"
echo "================================"
echo ""
echo "To use the web interface, open: $BASE_URL/ui"
