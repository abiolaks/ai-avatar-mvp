#!/bin/bash

# Configuration
OLLAMA_MODEL="llama3"

echo "🚀 Starting AI Avatar MVP..."

# Check if Ollama is running
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "❌ Error: Ollama is not running. Please start Ollama first."
    echo "   Run 'ollama serve' in a separate terminal."
    exit 1
fi

# Check if model exists
if ! curl -s http://127.0.0.1:11434/api/tags | grep -q "$OLLAMA_MODEL"; then
    echo "⚠️  Model '$OLLAMA_MODEL' not found in Ollama."
    echo "   Pulling model... (this may take a while)"
    ollama pull $OLLAMA_MODEL
fi

echo "✅ Environment checked."
echo "🎤 Initializing Audio..."

# Run the Python application
# Note: On Mac/Linux, we might need to pass audio devices carefully if using Docker.
# For local run:
python3 main.py
