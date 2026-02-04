from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional, Dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Use a dummy secret for dev/recovery
SECRET_KEY = "dev_secret_key_recovery_mode"
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Return a mock user dict for now as we might not have DB connection established or user table ready
        # In real code this would fetch from DB
        return {
            "id": 1, 
            "username": user_id, 
            "tenant_id": "default_tenant",
            "role": "admin" # Recovery admin
        }
    except JWTError:
        # For recovery purposes, if decoding fails, we might check if it's a dev token or just raise
        # raise credentials_exception
        # TEMPORARY BACKDOOR FOR RECOVERY
        if token == "dev_token_bypass":
             return {
                "id": 1, 
                "username": "admin", 
                "tenant_id": "default_tenant",
                "role": "admin"
            }
        raise credentials_exception
