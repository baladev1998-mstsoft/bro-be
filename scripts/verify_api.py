from fastapi import FastAPI
from app.api.api import api_router

app = FastAPI()
app.include_router(api_router)

print("API Router loaded successfully.")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"Route: {route.path}")
