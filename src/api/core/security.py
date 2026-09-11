import jwt
import time
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from api.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS

def create_jwt(username: str) -> str:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET environment variable is not configured.")
    payload = {
        "sub": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str) -> bool:
    if not JWT_SECRET:
        return False
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self.requests[key] = [t for t in self.requests[key] if now - t < self.window_seconds]
        if len(self.requests[key]) >= self.requests_limit:
            return False
        self.requests[key].append(now)
        return True

login_limiter = RateLimiter(requests_limit=5, window_seconds=60)

def get_current_user(request: Request):
    token = request.cookies.get("session_token")
    if not token or not verify_jwt(token):
        raise HTTPException(status_code=401, detail="Unauthorized session")
    return token
