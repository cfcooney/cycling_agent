def get_climb_extraction_prompt(schema: str, webpage_text: str) -> str:
    """
    Returns a formatted prompt for extracting climb data using the given schema and text.
    """
    return f"""
    You are a data extraction expert. Extract structured information about cycling climbs from the text below.

    Follow this schema:
    {schema}

    Text:
    {webpage_text}

    Return only valid JSON.
    """
