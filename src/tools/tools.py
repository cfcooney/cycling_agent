import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain.tools import tool, BaseTool
from serpapi import GoogleSearch
import requests
import time

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