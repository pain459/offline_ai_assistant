#!/bin/sh

ollama serve &
SERVER_PID=$!

# Wait for Ollama to become responsive
echo "Waiting for Ollama server to start..."
until curl -s http://localhost:11434 > /dev/null; do
  sleep 1
done

echo "Ollama is up. Checking for model..."

# Pull model if needed
if ! ollama list | grep -q "llama3"; then
  echo "Pulling llama3..."
  ollama pull llama3
else
  echo "Model 'llama3' already present. Skipping pull."
fi

wait $SERVER_PID
