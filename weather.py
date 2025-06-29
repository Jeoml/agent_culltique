from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return "its always sunny in San Francisco"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")