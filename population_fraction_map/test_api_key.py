"""
Quick test script to verify your API Ninjas API key works correctly.
Run this before running the full population map script.
"""

import os

import requests

API_KEY = os.getenv("API_NINJAS_API_KEY")


def test_api_connection():
    """Test if the API key works by fetching data for one country."""

    print("=" * 60)
    print("API Ninjas Connection Test")
    print("=" * 60)

    # Test the API with a simple request
    print(f"\n🔑 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print("\n📡 Testing API connection with 'United States'...")

    headers = {'X-Api-Key': API_KEY}
    params = {'country': 'United States'}

    try:
        response = requests.get('https://api.api-ninjas.com/v1/population', headers=headers, params=params, timeout=10)

        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if 'country_name' in data:
                print("\n✅ SUCCESS! API is working correctly.")
                print("\n📊 Sample Data Retrieved:")
                print(f"   Country: {data['country_name']}")

                if 'historical_population' in data and len(data['historical_population']) > 0:
                    latest = data['historical_population'][0]
                    print(f"   Latest Year: {latest['year']}")
                    print(f"   Population: {latest['population']:,}")
                    print(f"   Data Points Available: {len(data['historical_population'])}")

                print("\n✨ You're ready to run the full script!")
                return True
            else:
                print("\n⚠️  Unexpected response format")
                print(f"   Response: {data}")
                return False

        elif response.status_code == 401:
            print("\n❌ ERROR: Invalid API key")
            print("   Please check your API key and try again")
            return False

        elif response.status_code == 429:
            print("\n⚠️  Rate limit exceeded")
            print("   You've made too many requests. Wait a bit and try again.")
            return False

        else:
            print(f"\n❌ ERROR: Unexpected status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("   Please check your internet connection")
        return False

    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out")
        print("   The API took too long to respond. Try again.")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    test_api_connection()
    print("\n" + "=" * 60)
