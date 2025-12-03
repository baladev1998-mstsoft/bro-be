from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hash_from_db = "$2b$12$IhupC5X.fx2li6h7ttixB.IWlIg5l9fsUsXFBCT88oXgqdhaTZQuKa"
password = "admin123"

print(f"Testing password '{password}' against hash '{hash_from_db}'")

try:
    result = pwd_context.verify(password, hash_from_db)
    print(f"Verification result: {result}")
except Exception as e:
    print(f"Error: {e}")
