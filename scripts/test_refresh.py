import requests
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def login(email, password):
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": email, "password": password})
    if response.status_code == 200:
        data = response.json()["data"]
        logger.info("Login successful.")
        return data
    else:
        logger.error(f"Login failed for {email}: {response.text}")
        return None

def decode_token(token):
    response = requests.post(f"{BASE_URL}/api/v1/auth/decode-token", json={"token": token})
    if response.status_code == 200:
        payload = response.json()
        logger.info(f"Decoded payload: {payload}")
        return payload
    else:
        logger.error(f"Decode failed: {response.text}")
        return None

def refresh_token(refresh_token):
    response = requests.post(f"{BASE_URL}/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    if response.status_code == 200:
        data = response.json()["data"]
        logger.info("Refresh successful.")
        return data
    else:
        logger.error(f"Refresh failed: {response.text}")
        return None

def main():
    logger.info("Starting Refresh Token Test...")
    
    # 1. Login
    login_data = login("admin@bro.com", "password")
    if not login_data:
        return

    access_token = login_data["access_token"]
    refresh_token_str = login_data["refresh_token"]
    
    if not refresh_token_str:
        logger.error("FAILURE: No refresh token returned in login response.")
        return
    else:
        logger.info("SUCCESS: Refresh token present.")

    # 2. Check Access Token Claims (iat, exp)
    logger.info("Checking Access Token Claims...")
    payload = decode_token(access_token)
    if payload:
        if "iat" in payload and "exp" in payload:
            logger.info("SUCCESS: iat and exp present in access token.")
        else:
            logger.error("FAILURE: iat or exp missing in access token.")
            
    # 3. Test Refresh Flow
    logger.info("Testing Refresh Flow...")
    # Wait a second to ensure iat changes if we were to check that strictly, but mainly checking functionality
    time.sleep(1) 
    
    new_token_data = refresh_token(refresh_token_str)
    if new_token_data:
        new_access_token = new_token_data["access_token"]
        logger.info("Checking New Access Token...")
        new_payload = decode_token(new_access_token)
        if new_payload:
            logger.info("SUCCESS: New access token decoded successfully.")
            
            # Verify it's a new token (different iat or just valid)
            if new_payload["iat"] != payload["iat"]:
                 logger.info("SUCCESS: New token has different iat.")
            else:
                 logger.warning("WARNING: New token has same iat (might be too fast execution).")

if __name__ == "__main__":
    main()
