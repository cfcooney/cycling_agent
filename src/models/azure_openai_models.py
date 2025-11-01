import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import azure_endpoint

load_dotenv()

def get_azure_openai_model(model_name: str) -> AzureChatOpenAI:
    """Returns an AzureChatOpenAI model instance based on the model name."""
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    return AzureChatOpenAI(
        model_name=model_name,
        api_version=api_version,
        temperature=os.getenv("TEMPERATURE", 0.7),
        )