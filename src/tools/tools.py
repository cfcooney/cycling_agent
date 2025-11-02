import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain.tools import tool
from serpapi import GoogleSearch
import weatherapi
from weatherapi.rest import ApiException
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
    configuration = weatherapi.Configuration()
    configuration.api_key['key'] = os.getenv("WEATHERAPI_KEY")

    api_instance = weatherapi.APIsAPI(weatherapi.ApiClient(configuration))
    try:
        api_response = api_instance.get_current_weather(q=city)
    except ApiException as e:
        raise RuntimeError(f"get_weather function failed for {city}: {e}")
   
    condition = api_response.current.condition.text
    temp_c = api_response.current.temp_c
    humidity = api_response.current.humidity
    wind_kph = api_response.current.wind_kph

    return (f"The current weather in {city} is {condition} with a temperature of "
             f"{temp_c}°C, humidity at {humidity}%, and wind speed of {wind_kph} kph.")


@tool
def get_weather_forecast(city: str, days: int=3) -> List[str]:
    """Get the weather forecast for a given city for the next specified number of days.
    Args:
        city (str): The city to get the weather forecast for.
        days (int, optional): Number of days to forecast. Defaults to 3.
    Returns:
        str: A string describing the weather forecast.
    """
    configuration = weatherapi.Configuration()
    configuration.api_key['key'] = os.getenv("WEATHERAPI_KEY")

    api_instance = weatherapi.APIsAPI(weatherapi.ApiClient(configuration))
    try:
        api_response = api_instance.get_forecast_weather(q=city, days=days)
    except ApiException as e:
        raise RuntimeError(f"get_weather_forecast function failed for {city}: {e}")
    
    forecast_strings = []
    for day in api_response.forecast.forecastday:
        date = day.date
        condition = day.day.condition.text
        max_temp = day.day.maxtemp_c
        min_temp = day.day.mintemp_c
        chance_of_rain = day.day.daily_chance_of_rain

        forecast_strings.append(
            f"On {date}, expect {condition} with a high of {max_temp}°C and a low of {min_temp}°C. "
            f"Chance of rain: {chance_of_rain}%."
        )
        time.sleep(1)  # To avoid hitting rate limits  
    return forecast_strings
