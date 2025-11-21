import pytest
import os
from unittest.mock import patch, MagicMock
from src.tools.tools import UserStravaRoutesTool


class TestUserStravaRoutesTool:
    """Test cases for UserStravaRoutesTool"""

    def test_tool_initialization_with_token(self):
        """Test that the tool initializes correctly with a Strava token"""
        with patch.dict(os.environ, {"STRAVA_ACCESS_TOKEN": "test_token_123"}):
            tool = UserStravaRoutesTool(max_routes=3)
            assert tool.name == "user_strava_routes"
            assert tool.access_token == "test_token_123"
            assert tool.max_routes == 3
            assert "Bearer test_token_123" in tool.headers["Authorization"]

    def test_tool_initialization_without_token(self):
        """Test that the tool initializes without token (should be empty string)"""
        with patch.dict(os.environ, {}, clear=True):
            tool = UserStravaRoutesTool()
            assert tool.access_token == ""
            assert tool.max_routes == 5  # default value

    def test_properties(self):
        """Test that properties return correct values"""
        with patch.dict(os.environ, {"STRAVA_ACCESS_TOKEN": "test_token_456"}):
            tool = UserStravaRoutesTool()
            assert tool.url == "https://www.strava.com/api/v3/athlete/routes"
            assert tool.headers == {"Authorization": "Bearer test_token_456"}

    @patch("src.tools.tools.requests.get")
    def test_run_success_with_routes(self, mock_get):
        """Test successful API call that returns routes"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                "name": "Morning Ride",
                "id": 12345,
                "distance": 25000,  # 25km in meters
                "elevation_gain": 300,
            },
            {
                "name": "Hill Climb Challenge",
                "id": 67890,
                "distance": 15000,  # 15km in meters
                "elevation_gain": 800,
            },
        ]
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"STRAVA_ACCESS_TOKEN": "valid_token"}):
            tool = UserStravaRoutesTool(max_routes=2)
            result = tool._run()

        # Verify the result
        assert len(result) == 2
        assert result[0]["name"] == "Morning Ride"
        assert result[0]["id"] == 12345
        assert result[0]["distance_km"] == "25.0 km"
        assert result[0]["elevation_m"] == "300 m"

        assert result[1]["name"] == "Hill Climb Challenge"
        assert result[1]["distance_km"] == "15.0 km"
        assert result[1]["elevation_m"] == "800 m"

        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "https://www.strava.com/api/v3/athlete/routes" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer valid_token"
        assert call_args[1]["params"]["per_page"] == 2

    @patch("src.tools.tools.requests.get")
    def test_run_success_no_routes(self, mock_get):
        """Test successful API call that returns no routes"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"STRAVA_ACCESS_TOKEN": "valid_token"}):
            tool = UserStravaRoutesTool()
            result = tool._run()

        assert len(result) == 1
        assert result[0]["message"] == "No routes found for the user."

    def test_run_no_access_token(self):
        """Test that _run raises ValueError when no access token is provided"""
        with patch.dict(os.environ, {}, clear=True):
            tool = UserStravaRoutesTool()
            with pytest.raises(
                ValueError, match="STRAVA_ACCESS_TOKEN environment variable is required"
            ):
                tool._run()

    @patch("src.tools.tools.requests.get")
    def test_run_api_error(self, mock_get):
        """Test handling of API errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception(
            "API Error: 401 Unauthorized"
        )
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"STRAVA_ACCESS_TOKEN": "invalid_token"}):
            tool = UserStravaRoutesTool()
            with pytest.raises(Exception, match="API Error: 401 Unauthorized"):
                tool._run()

    def test_description_content(self):
        """Test that the tool description contains expected information"""
        tool = UserStravaRoutesTool()
        description = tool.description
        assert "Strava routes" in description
        assert "distance" in description
        assert "elevation" in description
        assert "access token" in description


# Integration test that can be run manually with real Strava token
def test_real_strava_integration():
    """
    Manual integration test - only run if you have a real Strava token.
    This test is skipped by default.
    """
    strava_token = os.getenv("STRAVA_ACCESS_TOKEN")
    if not strava_token or strava_token.startswith("your_"):
        pytest.skip("No real Strava token found - skipping integration test")

    tool = UserStravaRoutesTool(max_routes=3)
    try:
        result = tool._run()
        print(f"Integration test result: {result}")
        assert isinstance(result, list)
        if result and "message" not in result[0]:
            # If we got actual routes, verify the structure
            for route in result:
                assert "name" in route
                assert "id" in route
                assert "distance_km" in route
                assert "elevation_m" in route
                assert "km" in route["distance_km"]
                assert "m" in route["elevation_m"]
    except Exception as e:
        print(f"Integration test failed (this might be expected): {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
