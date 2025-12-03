import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def login(username, password):
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    return None

def test_access(token, endpoint, method="GET", expected_status=200):
    headers = {"Authorization": f"Bearer {token}"}
    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    elif method == "POST":
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json={})
    
    if response.status_code == expected_status:
        logger.info(f"SUCCESS: Access to {endpoint} with {method} returned {response.status_code} as expected.")
        return True
    else:
        logger.error(f"FAILURE: Access to {endpoint} with {method} returned {response.status_code}, expected {expected_status}. Response: {response.text}")
        return False

def main():
    logger.info("Starting RBAC Test...")
    
    # 1. Test Property Admin (Should have access)
    logger.info("Testing Property Admin...")
    token_prop_admin = login("propadmin@bro.com", "password")
    if token_prop_admin:
        test_access(token_prop_admin, "/api/v1/properties/", expected_status=200)
    
    # 2. Test Website User (Should NOT have access)
    logger.info("Testing Website User...")
    token_web_user = login("webuser@bro.com", "password")
    if token_web_user:
        test_access(token_web_user, "/api/v1/properties/", expected_status=403)
        
    # 3. Test System Admin (Should have access)
    logger.info("Testing System Admin...")
    token_sys_admin = login("admin@bro.com", "password")
    if token_sys_admin:
        test_access(token_sys_admin, "/api/v1/properties/", expected_status=200)

if __name__ == "__main__":
    main()
