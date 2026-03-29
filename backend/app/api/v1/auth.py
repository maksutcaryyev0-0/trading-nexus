from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import pyotp
from jose import jwt, JWTError

from app.core.config import settings

router  = APIRouter()
security = HTTPBearer()

DEMO_USERS = {
    "admin": {
        "password_hash": hashlib.sha256("nexus2024".encode()).hexdigest(),
        "role": "owner",
        "lang": "en",
        "timezone": "Europe/Moscow",
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str
    lang: str = "en"
    totp_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    lang: str
    timezone: str


def create_token(user_id: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub":  user_id,
        "role": role,
        "exp":  expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = DEMO_USERS.get(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    pwd_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if pwd_hash != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(req.username, user["role"])
    return TokenResponse(
        access_token=token,
        role=user["role"],
        lang=req.lang or user["lang"],
        timezone=user["timezone"],
    )


@router.post("/invite")
async def generate_invite(
    payload: dict,
    token: dict = Depends(verify_token),
):
    if token.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Owner only")
    code = secrets.token_urlsafe(8).upper()
    return {"invite_code": code, "expires_in": "24h"}


@router.get("/me")
async def get_me(token: dict = Depends(verify_token)):
    return {
        "user_id":  token["sub"],
        "role":     token["role"],
        "lang":     "en",
        "timezone": "Europe/Moscow",
    }


@router.get("/timezones")
async def get_timezones():
    from app.core.i18n import get_all_timezones
    return {"timezones": get_all_timezones()}


@router.get("/languages")
async def get_languages():
    return {
        "languages": [
            {"id": "en", "label": "English",  "dir": "ltr", "flag": "🇬🇧"},
            {"id": "ru", "label": "Русский",  "dir": "ltr", "flag": "🇷🇺"},
            {"id": "tr", "label": "Türkçe",   "dir": "ltr", "flag": "🇹🇷"},
            {"id": "ar", "label": "العربية",   "dir": "rtl", "flag": "🇸🇦"},
        ]
    }
