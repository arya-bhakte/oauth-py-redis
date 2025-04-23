import os
import redis
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID") 
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

def store_token():
    token_data = get_token()
    
    # Store the full token response as JSON
    r.setex(
        "oauth_token", 
        int(token_data.get("expires_in", 3600)),  
        json.dumps(token_data)
    )
    
    # For compatibility, also store just the access token
    r.setex(
        "oauth_access_token", 
        int(token_data.get("expires_in", 3600)),
        token_data["access_token"]
    )
    
    print(f"Token stored in Redis. Expires in {token_data.get('expires_in', 3600)} seconds.")
    print(f"Access token: {token_data['access_token'][:15]}... (truncated)")

def get_stored_token():
    """Retrieve and parse the stored token"""
    token_data = r.get("oauth_token")
    if token_data:
        return json.loads(token_data)
    return None

if __name__ == "__main__":
    store_token()