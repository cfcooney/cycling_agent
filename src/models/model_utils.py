def _get_deployment_id(model_name):
    """Returns the deployment ID based on the model name."""
    mapping = {
        "gpt-35-turbo": "gpt-35-turbo-16k",
        "gpt-4.1": "gpt-4.1",
        "gpt-4.1-mini": "gpt-4.1-mini",
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-4": "gpt-4",
        "o1-preview": "o1-preview",
        "o1-mini": "o1-mini",
    }
    if model_name == "gpt-4-alt":
        return "gpt4-turbo"  # Special case
    if model_name not in mapping:
        raise ValueError("Model name not recognized for deployment ID.")
    return mapping[model_name]
