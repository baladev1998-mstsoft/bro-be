import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def login(email, password):
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": email, "password": password})
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    else:
        logger.error(f"Login failed for {email}: {response.text}")
        return None

def test_decode(token):
    response = requests.post(f"{BASE_URL}/api/v1/auth/decode-token", json={"token": token})
    if response.status_code == 200:
        logger.info(f"SUCCESS: Decoded token payload: {response.json()}")
        return True
    else:
        logger.error(f"FAILURE: Decode token failed: {response.text}")
        return False

def main():
    logger.info("Starting Token Decode Test...")
    
    # 1. Login as System Admin
    logger.info("Logging in as System Admin...")
    token = login("admin@bro.com", "password")
    
    if token:
        # 2. Test Decode Endpoint
        logger.info("Testing Decode Endpoint...")
        test_decode(token)

if __name__ == "__main__":
    main()
