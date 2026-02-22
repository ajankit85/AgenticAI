import unittest
from unittest.mock import Mock

import weatherserver as ws


class MockResponse:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        return None

    def json(self):
        return self._json


class FakeSession:
    def __init__(self, responses):
        # responses should be consumed in order
        self._responses = list(responses)

    def get(self, url, timeout=10):
        if not self._responses:
            raise RuntimeError("No more fake responses")
        return MockResponse(self._responses.pop(0))


class WeatherServerTests(unittest.TestCase):
    def test_fetch_weather_sync_fahrenheit(self):
        geo = {"results": [{"name": "Dallas", "country": "United States", "latitude": 32.7767, "longitude": -96.7970}]}
        forecast = {"current_weather": {"temperature": 20.0, "windspeed": 12.3, "winddirection": 180, "time": "2026-02-22T12:00:00Z"}}

        session = FakeSession([geo, forecast])
        out = ws.fetch_weather_sync("Dallas, Texas", unit="F", session=session)
        self.assertIn("°F", out)
        self.assertIn("Dallas", out)

    def test_fetch_weather_sync_celsius(self):
        geo = {"results": [{"name": "London", "country": "United Kingdom", "latitude": 51.5074, "longitude": -0.1278}]}
        forecast = {"current_weather": {"temperature": 10.0, "windspeed": 5.2, "winddirection": 90, "time": "2026-02-22T12:00:00Z"}}

        session = FakeSession([geo, forecast])
        out = ws.fetch_weather_sync("London", unit="C", session=session)
        self.assertIn("°C", out)
        self.assertIn("London", out)


if __name__ == "__main__":
    unittest.main()
