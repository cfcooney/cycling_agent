# Ollama Function Calling Setup Guide

## The Problem
Llama2 models do NOT support function calling, which is required for your cycling agent's tools (bike rentals, weather).

## Solution: Use Function-Calling Compatible Models

### 1. Pull a Compatible Model
```bash
# Recommended (best balance of size and capability)
ollama pull llama3.1:8b

# Alternatives
ollama pull mistral:7b
ollama pull codellama:7b
```

### 2. Update Your .env File
```bash
MODEL_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

### 3. Test Your Agent
```bash
python cycling_chat.py
```

## Compatible Models for Function Calling

✅ **Works with Tools:**
- `llama3.1:8b` (recommended - 4.7GB)
- `llama3.1:70b` (if you have 40GB+ RAM)
- `mistral:7b` (3.8GB)
- `codellama:7b` (3.8GB)

❌ **Does NOT work with Tools:**
- `llama2:7b`
- `llama2:7b-chat`
- `llama2:13b-chat`

## Model Sizes
- `7b-8b models`: ~4-5GB RAM required
- `13b models`: ~8GB RAM required  
- `70b models`: ~40GB RAM required

## Quick Commands

```bash
# Check what models you have
ollama list

# Remove old incompatible model
ollama rm llama2:7b-chat

# Pull new compatible model
ollama pull llama3.1:8b

# Test if Ollama is running
curl http://localhost:11434/api/tags
```

## If You Want to Keep Llama2
You would need to modify the agent to work without function calling, but this significantly reduces functionality (no bike rental search, no weather data).