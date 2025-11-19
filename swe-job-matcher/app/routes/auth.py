import urllib.request
import json
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import users_collection, clerk

router = APIRouter()
security = HTTPBearer()

CLERK_JWKS_URL = "https://full-bee-63.clerk.accounts.dev/.well-known/jwks.json"

def get_clerk_public_key(token: str):
    try:
        # Extract the Key ID (kid) from the token header
        header = jwt.get_unverified_header(token)
        kid = header['kid']

        # Fetch valid keys from Clerk
        with urllib.request.urlopen(CLERK_JWKS_URL) as response:
            jwks = json.loads(response.read())

        # Find the matching key
        for key in jwks['keys']:
            if key['kid'] == kid:
                return RSAAlgorithm.from_jwk(json.dumps(key))
        
        raise Exception("Public key not found")
    except Exception as e:
        print(f"Key Fetch Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token signature")

async def get_user_id(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the JWT and returns the user_id (sub).
    """
    try:
        jwt_token = token.credentials
        public_key = get_clerk_public_key(jwt_token)

        # Decode & Verify
        payload = jwt.decode(
            jwt_token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        
        return payload["sub"]
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")

@router.post("/sync-user")
async def sync_user(user_id: str = Depends(get_user_id)):
    # Check if user already exists in Mongo DB
    user = users_collection.find_one({"_id": user_id})
    if user:
        return {"ok": True, "status": "EXISTS"}

    try:
        # Correct syntax for the Python SDK (v4+)
        user_data = clerk.users.get(user_id=user_id)
        
        # Safely get the primary email
        email = ""
        if user_data.email_addresses:
            email = user_data.email_addresses[0].email_address

        # Create the user in your Database
        new_user = {
            "_id": user_id,
            "email": email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
        }
        
        users_collection.insert_one(new_user)
        return {"ok": True, "status": "CREATED"}

    except Exception as e:
        print(f"Sync Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync user data")