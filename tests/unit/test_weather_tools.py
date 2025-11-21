import pytest
from unittest.mock import patch, MagicMock
import os
from src.tools.tools import get_weather_now, get_weather_forecast


class TestWeatherTools:
    @patch("src.tools.tools.requests.get")
    def test_get_weather_now_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "location": {"name": "London", "country": "UK"},
            "current": {
                "condition": {"text": "Sunny"},
                "temp_c": 20.0,
                "humidity": 50,
                "wind_kph": 15.0,
            },
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"WEATHERAPI_KEY": "test_key"}):
            result = get_weather_now.invoke({"city": "London"})

        assert "London, UK" in result
        assert "Sunny" in result
        assert "20.0°C" in result

    @patch("src.tools.tools.requests.get")
    def test_get_weather_forecast_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "forecast": {
                "forecastday": [
                    {
                        "date": "2023-10-01",
                        "day": {
                            "condition": {"text": "Rainy"},
                            "maxtemp_c": 15.0,
                            "mintemp_c": 10.0,
                            "daily_chance_of_rain": 80,
                        },
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"WEATHERAPI_KEY": "test_key"}):
            result = get_weather_forecast.invoke({"city": "London", "days": 1})

        assert len(result) == 1
        assert "2023-10-01" in result[0]
        assert "Rainy" in result[0]

    def test_weather_tools_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing WEATHERAPI_KEY"):
                get_weather_now.invoke({"city": "London"})

            with pytest.raises(ValueError, match="Missing WEATHERAPI_KEY"):
                get_weather_forecast.invoke({"city": "London"})
