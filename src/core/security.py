import bcrypt
from src.config import CONFIG
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

ALGOTITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, CONFIG.SECRET_KEY, algorithm=ALGOTITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[ALGOTITHM])
    except JWTError:
        return None