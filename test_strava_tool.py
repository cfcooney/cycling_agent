#!/usr/bin/env python3
"""
Simple test script for UserStravaRoutesTool
Run this script to test if your Strava tool is working correctly.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.tools.tools import UserStravaRoutesTool
    print("✅ Successfully imported UserStravaRoutesTool")
except ImportError as e:
    print(f"❌ Failed to import UserStravaRoutesToool: {e}")
    sys.exit(1)


def test_basic_functionality():
    """Test basic functionality of the Strava tool"""
    print("\n🧪 Testing basic functionality...")
    
    # Test 1: Tool initialization
    try:
        with patch.dict(os.environ, {'STRAVA_ACCESS_TOKEN': 'test_token_123'}):
            tool = UserStravaRoutesTool(max_routes=3)
            assert tool.name == "user_strava_routes"
            assert tool.access_token == "test_token_123"
            assert tool.max_routes == 3
            print("✅ Tool initialization: PASSED")
    except Exception as e:
        print(f"❌ Tool initialization: FAILED - {e}")
        return False
    
    # Test 2: Properties
    try:
        assert tool.url == "https://www.strava.com/api/v3/athlete/routes"
        assert "Bearer test_token_123" in tool.headers["Authorization"]
        print("✅ Properties: PASSED")
    except Exception as e:
        print(f"❌ Properties: FAILED - {e}")
        return False
    
    # Test 3: No token error
    try:
        with patch.dict(os.environ, {}, clear=True):
            tool_no_token = UserStravaRoutesTool()
            try:
                tool_no_token._run()
                print("❌ No token error test: FAILED - Should have raised ValueError")
                return False
            except ValueError as ve:
                if "STRAVA_ACCESS_TOKEN" in str(ve):
                    print("✅ No token error test: PASSED")
                else:
                    print(f"❌ No token error test: FAILED - Wrong error message: {ve}")
                    return False
    except Exception as e:
        print(f"❌ No token error test: FAILED - {e}")
        return False
    
    return True


def test_mocked_api_call():
    """Test with mocked API response"""
    print("\n🌐 Testing mocked API call...")
    
    try:
        # Mock the requests.get call
        with patch('src.tools.tools.requests.get') as mock_get:
            # Set up mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = [
                {
                    "name": "Test Route",
                    "id": 12345,
                    "distance": 20000,  # 20km in meters
                    "elevation_gain": 500
                }
            ]
            mock_get.return_value = mock_response
            
            # Test the tool
            with patch.dict(os.environ, {'STRAVA_ACCESS_TOKEN': 'valid_token'}):
                tool = UserStravaRoutesTool(max_routes=1)
                result = tool._run()
            
            # Verify result
            assert len(result) == 1
            assert result[0]["name"] == "Test Route"
            assert result[0]["id"] == 12345
            assert result[0]["distance_km"] == "20.0 km"
            assert result[0]["elevation_m"] == "500 m"
            
            print("✅ Mocked API call: PASSED")
            print(f"   Result: {result}")
            return True
            
    except Exception as e:
        print(f"❌ Mocked API call: FAILED - {e}")
        return False


def test_real_strava_token():
    """Test with real Strava token if available"""
    print("\n🔗 Testing with real Strava token...")
    
    strava_token = os.getenv("STRAVA_ACCESS_TOKEN")
    if not strava_token or strava_token.startswith("your_"):
        print("⚠️  No real Strava token found (this is okay for testing)")
        print("   To test with real data, set STRAVA_ACCESS_TOKEN in your .env file")
        return True
    
    try:
        tool = UserStravaRoutesTool(max_routes=3)
        result = tool._run()
        
        if result and "message" in result[0] and "No routes found" in result[0]["message"]:
            print("✅ Real Strava API call: PASSED (no routes found)")
            return True
        elif result and isinstance(result, list) and len(result) > 0:
            print("✅ Real Strava API call: PASSED")
            print(f"   Found {len(result)} routes:")
            for i, route in enumerate(result, 1):
                print(f"   {i}. {route['name']} - {route['distance_km']}, {route['elevation_m']}")
            return True
        else:
            print(f"❌ Real Strava API call: FAILED - Unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Real Strava API call: FAILED - {e}")
        print("   This might be due to invalid token or API issues")
        return False


def main():
    """Run all tests"""
    print("🚴 Testing UserStravaRoutesTool")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_basic_functionality():
        tests_passed += 1
    
    if test_mocked_api_call():
        tests_passed += 1
    
    if test_real_strava_token():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests PASSED! Your UserStravaRoutesTool is functional.")
        return 0
    else:
        print("⚠️  Some tests FAILED. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)