"""Weather tool for LangChain."""
from typing import Optional

import requests
from langchain_core.tools import tool


@tool
def get_weather(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    city: Optional[str] = None,
) -> dict:
    """
    Get the current weather at a location.

    You can provide either coordinates or a city name.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        city: City name (e.g., 'San Francisco', 'New York', 'London')

    Returns:
        Weather data dictionary
    """
    if city:
        # Geocode city to get coordinates
        coords = geocode_city(city)
        if not coords:
            return {"error": f'Could not find coordinates for "{city}". Please check the city name.'}
        latitude = coords["latitude"]
        longitude = coords["longitude"]
    elif latitude is None or longitude is None:
        return {
            "error": "Please provide either a city name or both latitude and longitude coordinates."
        }

    # Get weather data from Open-Meteo API
    try:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
                "hourly": "temperature_2m",
                "daily": "sunrise,sunset",
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        weather_data = response.json()

        if city:
            weather_data["cityName"] = city

        return weather_data
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}


def geocode_city(city: str) -> Optional[dict]:
    """
    Geocode city name to coordinates.

    Args:
        city: City name

    Returns:
        Dictionary with latitude and longitude, or None
    """
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )

        if not response.ok:
            return None

        data = response.json()

        if not data.get("results") or len(data["results"]) == 0:
            return None

        result = data["results"][0]
        return {"latitude": result["latitude"], "longitude": result["longitude"]}
    except requests.RequestException:
        return None

