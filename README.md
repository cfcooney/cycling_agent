# Cycling Agent 🚴‍♂️

A conversational AI assistant specializing in cycling advice, bike rentals, weather information, and local cycling recommendations. Built with LangChain and supports both cloud (Azure OpenAI) and local (Ollama) language models.

## Features

- 🚴 **Bike Rental Search**: Find bike shops and rentals in any city
- 🌤️ **Weather Information**: Current weather and forecasts for cycling planning
- 💬 **Conversational Interface**: Rich command-line chat with history and commands
- 🌐 **Multi-Model Support**: Works with Azure OpenAI, Ollama (Llama models), and more
- 🔧 **Tool Integration**: Uses real-time APIs for factual information

## Project Structure

```
cycling_agent/
├── src/
│   ├── agents/          # Agent implementations
│   ├── models/          # Model configurations (Azure OpenAI, Ollama)
│   ├── prompts/         # Prompt templates
│   ├── tools/           # Custom tools (bike rentals, weather)
│   └── utils/           # Utility functions
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docs/                # Documentation and setup guides
├── cycling_chat.py      # Main entry point for conversational agent
└── requirements.txt     # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux

# Install Python packages
pip install -r requirements.txt
```

### 2. Choose Your Model Provider

You can use either cloud-based Azure OpenAI or local Ollama models:

#### Option A: Azure OpenAI (Cloud)
1. Get Azure OpenAI credentials from Azure Portal
2. Create `.env` file with your credentials:
   ```bash
   MODEL_PROVIDER=azure_openai
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   ```

#### Option B: Ollama (Local) - **Recommended for Privacy**
1. **Install Ollama**: Download from https://ollama.ai/
2. **Pull a function-calling compatible model**:
   ```bash
   ollama pull llama3.1:8b
   ```
3. **Configure environment**:
   ```bash
   MODEL_PROVIDER=ollama
   OLLAMA_MODEL=llama3.1:8b
   ```

### 3. Set Up API Keys (Optional)

For enhanced functionality, get free API keys:

- **Weather API**: Sign up at https://www.weatherapi.com/ (1M free calls/month)
- **Search API**: Sign up at https://serpapi.com/ (100 free searches/month)

Add to your `.env` file:
```bash
WEATHERAPI_KEY=your_weatherapi_key_here
SERPAPI_KEY=your_serpapi_key_here
```

### 4. Run the Agent

```bash
python cycling_chat.py
```

## Ollama Setup (Detailed)

### Why Ollama?
- ✅ **Privacy**: All processing happens locally
- ✅ **No API costs**: Free unlimited usage
- ✅ **Offline capability**: Works without internet
- ✅ **Fast**: Good performance on modern hardware

### Installation Steps

1. **Install Ollama**:
   ```bash
   # Windows (PowerShell)
   winget install Ollama.Ollama
   
   # Or download from: https://ollama.ai/
   ```

2. **Pull a compatible model**:
   ```bash
   # Recommended (4.7GB, good balance of speed and quality)
   ollama pull llama3.1:8b
   
   # Alternatives:
   ollama pull mistral:7b      # 3.8GB, faster
   ollama pull llama3.1:70b    # 40GB, best quality (requires 64GB+ RAM)
   ```

3. **Verify installation**:
   ```bash
   ollama list
   ollama run llama3.1:8b "Hello, how are you?"
   ```

4. **Configure your cycling agent**:
   Create `.env` file:
   ```bash
   MODEL_PROVIDER=ollama
   OLLAMA_MODEL=llama3.1:8b
   OLLAMA_BASE_URL=http://localhost:11434
   TEMPERATURE=0.7
   ```

### Important: Function Calling Compatibility

⚠️ **Not all models support tools/function calling** (required for bike search and weather):

✅ **Compatible Models:**
- `llama3.1:8b` (recommended)
- `llama3.1:70b`
- `mistral:7b`
- `codellama:7b`

❌ **Incompatible Models:**
- `llama2:7b-chat` (will cause "does not support tools" error)
- `llama2:13b-chat`

### Hardware Requirements

| Model Size | RAM Required | Speed | Quality |
|------------|--------------|-------|---------|
| 7b-8b      | 8GB+        | Fast  | Good    |
| 13b        | 16GB+       | Medium| Better  |
| 70b        | 64GB+       | Slow  | Best    |

## Usage Examples

### Basic Conversation
```
🚴 You: Hello, I'm planning a cycling trip to Barcelona

🤖 Assistant: Great! I'd be happy to help you plan your cycling trip to Barcelona. 
I can help you find bike rentals, check the weather, and suggest cycling routes. 
What specific information would you like to know?

🚴 You: Find bike rentals near Park Güell

🤖 Assistant: Let me find bike rental options near Park Güell in Barcelona...
[Searches and returns local bike shops with ratings, addresses, and contact info]
```

### Available Commands
- `/help` - Show help and available commands
- `/clear` - Clear conversation history  
- `/history` - Show conversation history
- `/quit` or `/exit` - Exit the application

### Switching Between Models
```bash
# Use Azure OpenAI
MODEL_PROVIDER=azure_openai python cycling_chat.py

# Use local Ollama
MODEL_PROVIDER=ollama python cycling_chat.py
```

## Troubleshooting

### Common Issues

1. **"does not support tools" error**: 
   - Use `llama3.1:8b` instead of `llama2:7b-chat`
   - See function calling compatibility section above

2. **"401 Unauthorized" weather error**:
   - Get a free API key from https://www.weatherapi.com/
   - Add `WEATHERAPI_KEY=your_actual_key` to `.env`

3. **Ollama connection error**:
   ```bash
   # Make sure Ollama is running
   ollama serve
   
   # Check if model is available
   ollama list
   ```

4. **Model not found**:
   ```bash
   # Pull the model first
   ollama pull llama3.1:8b
   ```

### Performance Tips
- Use smaller models (7b-8b) for faster responses
- Ensure adequate RAM for your chosen model size
- Close other memory-intensive applications
- Consider GPU acceleration if available

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Tools
1. Create tool function in `src/tools/tools.py`
2. Use `@tool` decorator from LangChain
3. Add tool to agent in `src/agents/conversational_agent.py`

### Project Documentation
- [Ollama Function Calling Fix](docs/ollama_function_calling_fix.md)
- [Llama2 Integration Guide](docs/llama2_setup.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

[Add your license here]
