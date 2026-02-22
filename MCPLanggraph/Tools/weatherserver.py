from mcp.server.fastmcp import FastMCP
import requests
from urllib.parse import quote_plus
from typing import Optional, Dict, Any

mcp = FastMCP("WeatherServer")


def geocode(city: str, session: Optional[requests.Session] = None) -> Optional[Dict[str, Any]]:
    """Return the best geocoding result for `city`, or None on not found.

    `session` may be a requests-like object with a `.get()` method (injected for testing).
    """
    session = session or requests
    q = quote_plus(city)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1"
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results")
    if not results:
        return None
    return results[0]


def get_current_weather(lat: float, lon: float, session: Optional[requests.Session] = None, unit: str = "F") -> Optional[Dict[str, Any]]:
    """Return the `current_weather` block from Open-Meteo, or None on error.

    If `unit` == "F", request `temperature_unit=fahrenheit` so the API returns °F.
    """
    session = session or requests
    # include temperature_unit when Fahrenheit is requested so API returns °F
    temp_unit_param = "&temperature_unit=fahrenheit" if str(unit).upper() == "F" else ""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current_weather=true&timezone=auto{temp_unit_param}"
    )
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("current_weather")


def format_weather(place: Dict[str, Any], cw: Dict[str, Any], unit: str = "F") -> str:
    """Return a human-readable one-line weather summary.

    - `place` comes from `geocode()`
    - `cw` is the `current_weather` dict from Open-Meteo
    - `unit` may be "C" or "F"; default is "F" for Fahrenheit
    """
    location = place.get("name") or ""
    country = place.get("country") or ""
    lat = place.get("latitude")
    lon = place.get("longitude")

    temp = cw.get("temperature")
    windspeed = cw.get("windspeed")
    winddir = cw.get("winddirection")
    observed = cw.get("time")

    parts = []
    loc_part = location
    if country:
        loc_part = f"{loc_part}, {country}"
    parts.append(loc_part)

    if lat is not None and lon is not None:
        parts.append(f"({lat}, {lon})")

    weather_bits = []
    if temp is not None:
        try:
            t = float(temp)
            # If we asked the API for Fahrenheit, temp is already °F
            if str(unit).upper() == "F":
                weather_bits.append(f"{t:.1f}°F")
            else:
                # Treat t as Celsius and also show Fahrenheit in parentheses
                t_c = t
                t_f = t_c * 9.0 / 5.0 + 32.0
                weather_bits.append(f"{t_c:.1f}°C ({t_f:.1f}°F)")
        except Exception:
            # Fallback: display raw value
            if str(unit).upper() == "F":
                weather_bits.append(f"{temp}°F")
            else:
                weather_bits.append(f"{temp}°C")

    if windspeed is not None:
        weather_bits.append(f"wind {windspeed} km/h")
    if winddir is not None:
        weather_bits.append(f"from {winddir}°")

    if weather_bits:
        parts.append(", ".join(weather_bits))

    if observed:
        parts.append(f"observed at {observed}")

    return " — ".join([p for p in parts if p])


@mcp.tool()
async def fetch_weather(city: str, unit: str = "F") -> str:
    """MCP tool entrypoint. Returns a single formatted string (errors are strings)."""
    try:
        place = geocode(city)
        if not place:
            return f"Error: No geocoding result for '{city}'"

        lat = place.get("latitude")
        lon = place.get("longitude")
        if lat is None or lon is None:
            return f"Error: Missing coordinates for '{city}'"

        cw = get_current_weather(lat, lon, unit=unit)
        if not cw:
            return "Error: No current weather in response"

        return format_weather(place, cw, unit=unit)
    except Exception as e:
        return f"Error: {e}"


def fetch_weather_sync(city: str, unit: str = "F", session: Optional[requests.Session] = None) -> str:
    """Synchronous convenience wrapper for local testing (bypasses MCP).

    Allows injecting a `session` for unit tests.
    """
    try:
        place = geocode(city, session=session)
        if not place:
            return f"Error: No geocoding result for '{city}'"
        lat = place.get("latitude")
        lon = place.get("longitude")
        if lat is None or lon is None:
            return f"Error: Missing coordinates for '{city}'"
        cw = get_current_weather(lat, lon, session=session, unit=unit)
        if not cw:
            return "Error: No current weather in response"
        return format_weather(place, cw, unit=unit)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Quick manual test - runs the MCP server
    mcp.run(transport="streamable-http")
