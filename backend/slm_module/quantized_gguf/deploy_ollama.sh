#!/bin/bash
# ============================================================
# Ollama Edge Deployment — Smart Traffic Alert Generator
# Run this script after quantization is complete
# ============================================================

# Step 1: Install Ollama (one-time)
curl -fsSL https://ollama.ai/install.sh | sh

# Step 2: Start Ollama server
ollama serve &
sleep 3

# Step 3: Create the traffic alert model from our Modelfile
cd slm_module/quantized_gguf
ollama create smart-traffic-alerts -f Modelfile

# Step 4: Test the deployment
ollama run smart-traffic-alerts \
  "generate traffic alert: road=Anna Salai; type=accident; severity=high"

# Expected output:
# ALERT [HIGH] Anna Salai: Avoid the area immediately, expect significant delays.
# Expected delay: 25 minutes.

# Step 5: Verify the Ollama API (OpenAI-compatible)
curl http://localhost:11434/api/generate -d '{
  "model": "smart-traffic-alerts",
  "prompt": "generate traffic alert: road=GST Road; type=flooding; severity=critical",
  "stream": false
}'

echo "Ollama deployment complete. API available at http://localhost:11434"
