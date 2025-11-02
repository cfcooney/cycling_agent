# Llama2 Integration Guide

This document explains how to use Llama2 as an open-source alternative in your cycling agent.

## Option 1: Ollama (Recommended)

Ollama is the easiest way to run Llama2 locally.

### Setup Steps:

1. **Install Ollama:**
   ```bash
   # Download and install from: https://ollama.ai/
   # Or using PowerShell:
   winget install Ollama.Ollama
   ```

2. **Pull Llama2 model:**
   ```bash
   ollama pull llama2
   # Or specific versions:
   ollama pull llama2:7b
   ollama pull llama2:13b
   ollama pull llama2:70b
   ```

3. **Install Python dependencies:**
   ```bash
   pip install langchain-community
   ```

4. **Configure environment:**
   ```bash
   # In your .env file:
   MODEL_PROVIDER=ollama
   OLLAMA_MODEL=llama2
   OLLAMA_BASE_URL=http://localhost:11434
   ```

5. **Run your agent:**
   ```bash
   python cycling_chat.py
   ```

### Available Llama2 Models:
- `llama2` (7B parameters - fastest)
- `llama2:13b` (13B parameters - better quality)
- `llama2:70b` (70B parameters - best quality, requires more RAM)
- `llama2:7b-chat` (Chat-optimized versions)
- `llama2:13b-chat`

## Option 2: HuggingFace Transformers

For more control, run models directly with HuggingFace.

### Setup Steps:

1. **Install dependencies:**
   ```bash
   pip install transformers torch accelerate
   ```

2. **Configure environment:**
   ```bash
   # In your .env file:
   MODEL_PROVIDER=huggingface
   HF_MODEL=meta-llama/Llama-2-7b-chat-hf
   ```

3. **Note:** Requires HuggingFace Hub access and potentially GPU for good performance.

## Hardware Requirements

### Ollama:
- **7B model**: 8GB RAM minimum
- **13B model**: 16GB RAM minimum  
- **70B model**: 64GB RAM minimum

### Performance Tips:
- Use smaller models (7B) for development
- Consider GPU acceleration for better performance
- Ollama automatically manages memory and optimization

## Usage Examples

### Switch between models:
```bash
# Use Azure OpenAI
MODEL_PROVIDER=azure_openai python cycling_chat.py

# Use local Llama2
MODEL_PROVIDER=ollama python cycling_chat.py

# Use HuggingFace
MODEL_PROVIDER=huggingface python cycling_chat.py
```

## Benefits of Llama2 Integration

1. **Privacy**: No data sent to external APIs
2. **Cost**: No per-token charges
3. **Customization**: Fine-tune for cycling domain
4. **Offline**: Works without internet
5. **Control**: Full control over model behavior

## Considerations

1. **Performance**: May be slower than cloud APIs
2. **Quality**: Smaller models may have lower quality responses
3. **Resources**: Requires local computational resources
4. **Setup**: More complex initial setup

## Troubleshooting

### Common Issues:

1. **Ollama not running:**
   ```bash
   # Start Ollama service
   ollama serve
   ```

2. **Model not found:**
   ```bash
   # Pull the model
   ollama pull llama2
   ```

3. **Memory issues:**
   - Use smaller model variants
   - Close other applications
   - Consider cloud deployment

### Performance Optimization:

1. **Use appropriate model size for your hardware**
2. **Enable GPU acceleration if available**
3. **Adjust temperature and other parameters**
4. **Consider model quantization for speed**