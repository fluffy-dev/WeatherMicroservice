from unittest.mock import patch, MagicMock
import pytest
import httpx

from src.weather.client import OpenWeatherClient


@pytest.mark.asyncio
async def test_get_weather_success():
    """Test successful data fetching from external API."""

    mock_response_data = {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {
            "temp": 15.5,
            "humidity": 72,
            "pressure": 1012
        }
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=MagicMock) as mock_get:

        with patch("httpx.AsyncClient", autospec=True) as mock_client_cls:
            mock_instance = mock_client_cls.return_value
            mock_instance.__aenter__.return_value.get.return_value = mock_response

            client = OpenWeatherClient()
            result = await client.get_weather("London")

            assert result is not None
            assert result["city"] == "London"
            assert result["temperature"] == 15.5
            assert result["country"] == "GB"


@pytest.mark.asyncio
async def test_get_weather_failure():
    """Test handling of HTTP errors from external API."""

    with patch("httpx.AsyncClient", autospec=True) as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.__aenter__.return_value.get.side_effect = httpx.HTTPError("Connection failed")

        client = OpenWeatherClient()
        result = await client.get_weather("UnknownCity")

        assert result is None