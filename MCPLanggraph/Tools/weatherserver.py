from mcp.server.fastmcp import FastMCP

mcp=FastMCP("WeatherServer")

@mcp.tool()
async def get_weather(location:str)->str:
    """Get weather for the location."""
    return "It's always warm in Texas."

if __name__=="__main__":
    mcp.run(transport="streamable-http")
