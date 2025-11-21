import pytest
from unittest.mock import patch, MagicMock
import os
from src.tools.tools import find_bike_rentals


class TestRentalTools:
    @patch("src.tools.tools.GoogleSearch")
    def test_find_bike_rentals_success(self, mock_search_class):
        # Mock GoogleSearch instance
        mock_search_instance = MagicMock()
        mock_search_class.return_value = mock_search_instance

        # Mock results
        mock_search_instance.get_dict.return_value = {
            "local_results": [
                {
                    "title": "Best Bikes",
                    "gps_coordinates": {"latitude": 51.5, "longitude": -0.1},
                    "rating": 4.5,
                    "type": "Bike Rental",
                    "address": "123 Main St",
                    "open_state": "Open now",
                    "phone": "123-456-7890",
                    "website": "http://example.com",
                }
            ]
        }

        with patch.dict(os.environ, {'SERPAPI_KEY': 'test_key'}):
            result = find_bike_rentals.invoke({"city": "London"})
            
        assert len(result) == 1
        assert result[0]["title"] == "Best Bikes"
        assert result[0]["rating"] == 4.5
        
    @patch('src.tools.tools.GoogleSearch')
    def test_find_bike_rentals_no_results(self, mock_search_class):
        mock_search_instance = MagicMock()
        mock_search_class.return_value = mock_search_instance
        mock_search_instance.get_dict.return_value = {}
        
        with patch.dict(os.environ, {'SERPAPI_KEY': 'test_key'}):
            result = find_bike_rentals.invoke({"city": "Nowhere"})
            
        assert len(result) == 1
        assert "No bike rentals found" in result[0]["message"]

    def test_find_bike_rentals_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing SERPAPI_API_KEY"):
                find_bike_rentals.invoke({"city": "London"})
