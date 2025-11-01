import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain.tools import tool
from serpapi import GoogleSearch

load_dotenv()   

@tool
def find_bike_rentals(city: str, locality: str="") -> List[Dict]:
    """Find bike rental shops in a given location.
    Args:
        city (str): The city to search in.
        locality (str, optional): The specific locality within the city. Defaults to empty string.
    Returns:
        list[dict]: A list of dictionaries with bike rental shop details.
    """
    location = f"{city}, {locality}" if locality else city

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("Missing SERPAPI_API_KEY environment variable")
    

    params = {
        "engine": "google_maps",
        "q": f"{location} bike rental",
        "location": location,
        "api_key": api_key,
        "num": 3
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    local_results = results.get("local_results", [])
    if not local_results:
        return [{"message": f"No bike rentals found near {location}."}]

    return_details = []
    for shop in local_results[:5]:
        details = {
            "title": shop.get("title"),
            "gps_coordinates": shop.get("gps_coordinates"),
            "rating": shop.get("rating"),
            "type": shop.get("type"),
            "address": shop.get("address"),
            "open_state": shop.get("open_state"),
            "phone": shop.get("phone"),
            "website": shop.get("website"),
        }
        return_details.append(details)
    return return_details