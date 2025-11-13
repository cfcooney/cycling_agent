import os
from langchain_ollama import ChatOllama, OllamaLLM
from typing import Optional, Union 
import ollama

def get_ollama_model(model_name: str, chat: bool = True) -> Optional[Union[ChatOllama, OllamaLLM]]:
    """Returns an Ollama model instance based on the model name.
    
    Note: For tools/function calling, use models like:
    - llama3.1:8b (recommended)
    - mistral:7b
    - codellama:7b
    
    Models like llama2:7b-chat do NOT support function calling.
    """
    if chat:
        return ChatOllama(
            model=model_name,
            temperature=0.7,
            num_predict=256
            )
    else:
        OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaLLM(
            model=model_name,
            temperature=0.7,
            base_url=OLLAMA_BASE_URL
            )