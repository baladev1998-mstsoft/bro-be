import requests
import json

BASE_URL = "http://localhost:8008/api/v1/properties/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQ2NzI2MjIsInN1YiI6IjdiMjlkZTBkLTRmNjQtNDllZi1hYmRlLTQyN2U4ZDk1ZTA0MSIsImlhdCI6MTc2NDY3MDgyMiwiZW1haWwiOiJhZG1pbkBicm8uY29tIiwicGhvbmUiOm51bGwsIm5hbWUiOiJTeXN0ZW0gQWRtaW4iLCJyb2xlcyI6W3sicm9sZSI6IlNZU1RFTV9BRE1JTiIsInNjb3BlIjoiZ2xvYmFsIn1dLCJkZWZhdWx0X3RlbmFudCI6bnVsbCwidHlwZSI6ImFjY2VzcyJ9.L0lEsVgr19twxCXX-kKXPztVgqXgM07_3f9GC4GGtcg"

def create_property(dest_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "King Cliff",
        "slug": "king-cliff-final", # Changed slug
        "property_type": "hotel",
        "address": "Havelock road, Ooty, 643001",
        "contact_email": "kingcliffbooking@gmail.com",
        "contact_phone": "9865443322",
        "overview": "A house with a history...",
        "rating": 4.5,
        "is_published": False,
        "destination_id": dest_id
    }
    
    print("Creating property...")
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def get_destination_id():
    url = "http://localhost:8008/api/v1/public/destinations"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                return data[0]["id"]
    except Exception as e:
        print(f"Error fetching destination: {e}")
    return "943b9885-78ac-4124-b524-a3ca7bc81072" # Fallback

if __name__ == "__main__":
    dest_id = get_destination_id()
    create_property(dest_id)
