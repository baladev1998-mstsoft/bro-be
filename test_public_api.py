import requests
import json

BASE_URL = "http://localhost:8001/api/v1/public"

def test_destinations():
    print("Testing GET /destinations...")
    try:
        response = requests.get(f"{BASE_URL}/destinations")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get("data", [])
            print("Response:")
            print(json.dumps(response.json(), indent=2))
            if data:
                return data[0]["id"]
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return None

def test_properties(destination_id):
    print(f"\nTesting GET /destinations/{destination_id}/properties...")
    try:
        response = requests.get(f"{BASE_URL}/destinations/{destination_id}/properties")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    dest_id = test_destinations()
    if dest_id:
        test_properties(dest_id)
    else:
        print("No destinations found or failed to fetch destinations.")
