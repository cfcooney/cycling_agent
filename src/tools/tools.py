import os
import requests
import time
import json
import ollama
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List, Dict
from langchain.tools import tool, BaseTool
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from pydantic.v1 import BaseModel, Field
from typing import Optional, List
from prompts.extraction_prompt import get_climb_extraction_prompt


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


@tool
def get_weather_now(city: str) -> str:
    """Get the current weather for a given city. This is a specific tool for real-time weather information.
    Args:
        city (str): The city to get the weather for.
    Returns:
        str: A string describing the current weather in a specific location.
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        raise ValueError("Missing WEATHERAPI_KEY environment variable")
    
    try:
        # Using WeatherAPI.com (free tier available)
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": city,
            "aqi": "no"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        location = data['location']['name']
        country = data['location']['country']
        condition = data['current']['condition']['text']
        temp_c = data['current']['temp_c']
        humidity = data['current']['humidity']
        wind_kph = data['current']['wind_kph']
        
        return (f"The current weather in {location}, {country} is {condition} with a temperature of "
                f"{temp_c}°C, humidity at {humidity}%, and wind speed of {wind_kph} kph.")
                
    except requests.RequestException as e:
        raise RuntimeError(f"Weather API request failed for {city}: {e}")
    except KeyError as e:
        raise RuntimeError(f"Unexpected weather API response format: {e}")


@tool
def get_weather_forecast(city: str, days: int=3) -> List[str]:
    """Get the weather forecast for a given city for the next specified number of days.
    Args:
        city (str): The city to get the weather forecast for.
        days (int, optional): Number of days to forecast. Defaults to 3.
    Returns:
        List[str]: A list of strings describing the weather forecast for each day.
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        raise ValueError("Missing WEATHERAPI_KEY environment variable")
    
    # Limit days to API constraints (usually max 10 days for free tier)
    days = min(days, 7)
    
    try:
        # Using WeatherAPI.com forecast endpoint
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": api_key,
            "q": city,
            "days": days,
            "aqi": "no",
            "alerts": "no"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        forecast_strings = []
        for day in data['forecast']['forecastday']:
            date = day['date']
            condition = day['day']['condition']['text']
            max_temp = day['day']['maxtemp_c']
            min_temp = day['day']['mintemp_c']
            chance_of_rain = day['day']['daily_chance_of_rain']
            
            forecast_strings.append(
                f"On {date}, expect {condition} with a high of {max_temp}°C and a low of {min_temp}°C. "
                f"Chance of rain: {chance_of_rain}%."
            )
            time.sleep(0.1)  # Small delay to be respectful to the API
            
        return forecast_strings
        
    except requests.RequestException as e:
        raise RuntimeError(f"Weather forecast API request failed for {city}: {e}")
    except KeyError as e:
        raise RuntimeError(f"Unexpected weather forecast API response format: {e}")



class UserStravaRoutesTool(BaseTool):
    """Tool to get user's Strava routes. Currently requires valid access token and only enables access to athletes routes."""
    name: str = "user_strava_routes"
    description: str = (
        "Get a list of the user's Strava routes. Returns the name, ID, distance (in km), and elevation gain (in meters) of each route. "
        "Requires a valid Strava access token. "
    )
    
    # Declare all fields with type annotations
    access_token: str = ""
    max_routes: int = 5
    
    def __init__(self, max_routes: int = 5, **kwargs):
        # Initialize the parent class first
        super().__init__(**kwargs)
        # Set field values
        self.access_token = os.getenv("STRAVA_ACCESS_TOKEN", "")
        self.max_routes = max_routes
    
    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}
    
    @property
    def url(self) -> str:
        return "https://www.strava.com/api/v3/athlete/routes"

    def _run(self, query: str = "") -> List[Dict]:
        if not self.access_token:
            raise ValueError("STRAVA_ACCESS_TOKEN environment variable is required")
            
        params = {"per_page": self.max_routes}
        response = requests.get(self.url, headers=self.headers, params=params)
        response.raise_for_status()
        routes = response.json()
        if not routes:
            return [{"message": "No routes found for the user."}]
        result = []
        for r in routes:
            result.append({
                "name": r["name"],
                "id": r["id"],
                "distance_km": f"{r['distance']/1000:.1f} km",
                "elevation_m": f"{r['elevation_gain']} m"
            })
        return result
    

@tool
def find_cycling_climb_articles(location: str, radius_km: int = 50) -> List[str]:
    """Find cycling climbs near a specified geographic location.
    Args:
        location (str): The geographic location to search near (e.g., city name or coordinates).
        radius_km (int, optional): The search radius in kilometers. Defaults to 50 km.
    Returns:
        List[str]: A list of URLs to articles about cycling climbs near the specified location.
    """
    if not os.getenv("SERPAPI_KEY"):
        return ["SERPAPI_KEY environment variable not set."]
    
    params = {
        "engine": "google",  # Use the general Google search engine
        "q": f"famous cycling climbs within {radius_km} km of {location} stats",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    organic_results = results.get("organic_results", [])
    if not organic_results:
        return [f"No search results found for cycling climbs near {location}."]

    
    return [result["link"] for result in organic_results[:3] if "link" in result]


class Climb(BaseModel):
    name: str = Field(description="Name of the climb")
    location: Optional[str] = Field(description="Location of the climb")
    distance_km: Optional[float] = Field(description="Distance of the climb in kilometers")
    elevation_gain_m: Optional[int] = Field(description="Elevation gain of the climb in meters")
    average_gradient: Optional[float] = Field(description="Average gradient of the climb in percentage")
    max_gradient: Optional[float] = Field(default=None,
                                          description="Maximum gradient of the climb in percentage")
    
class ClimbList(BaseModel):
    climbs: List[Climb]

@tool
def scrape_and_extract_climb_stats(url: str) -> List[dict]:
    """Scrape a webpage for cycling climb statistics and extract structured data
    using a LLM prompted for this task.
    
    Args:
        url (str): The URL of the webpage to scrape.
    
        Returns: List[dict]: A list of dictionaries containing climb statistics.
    """
    # 1. Scrape the webpage content
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text_content = soup.get_text(separator=' ', strip=True)
        # Limit content size to avoid excessive token usage
        text_content = text_content[:8000]

    except requests.RequestException as e:
        return [f"Error fetching URL: {e}"]

    prompt = get_climb_extraction_prompt(
        schema=ClimbList.schema_json(indent=2),
        webpage_text=text_content
    )
    
    # --- Call Ollama ---
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
        )
    output = response["message"]["content"].strip()
    
    try:
        data = json.loads(output)

        # Handle full schema wrapper if present
        if "properties" in data and "climbs" in data["properties"]:
            climbs_data = data["properties"]["climbs"]
        elif "climbs" in data:
            climbs_data = data["climbs"]
        else:
            # fallback if output structure is unexpected
            climbs_data = []

        # Convert each climb dict to Climb model (handles optional fields)
        climbs_validated = [Climb(**c).dict() for c in climbs_data]

        return climbs_validated

    except json.JSONDecodeError:
        # If parsing fails, return raw output for inspection
        return ["Error parsing JSON from LLM output", output]


