from mcp.server.fastmcp import FastMCP

server = FastMCP("weather-server")


@server.tool()
def get_weather(city: str) -> str:
    """
    Get weather information for a city.
    """
    weather_data = {
        "Princeton": "Sunny, 75F",
        "Seattle": "Cloudy, 60F",
        "Austin": "Sunny, 85F",
    }

    return weather_data.get(city, "Weather information unavailable")


if __name__ == "__main__":
    print("Server running...")
    server.run()
