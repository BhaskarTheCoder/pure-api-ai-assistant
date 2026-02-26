import json
import urllib.request
import urllib.parse
from mcp.server.fastmcp import FastMCP

# Create an MCP server named "Weather Server"
mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    try:
        # 1. Geocoding
        encoded_city = urllib.parse.quote(city)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}"
        
        with urllib.request.urlopen(geo_url) as response:
            geo_data = json.loads(response.read().decode())
            
        if "results" not in geo_data:
            return f"City '{city}' not found."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # 2. Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        with urllib.request.urlopen(weather_url) as response:
            weather_data = json.loads(response.read().decode())

        temp = weather_data["current_weather"]["temperature"]
        return f"The current temperature in {city} is {temp}°C."
    except Exception as e:
        return f"Failed to get weather: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server using Standard IO (stdio) for communication
    print("Starting Weather MCP Server...")
    mcp.run(transport='stdio')
