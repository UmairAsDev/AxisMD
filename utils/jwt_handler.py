from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from tools.settings import settings


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=60*24)):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    print(f"Token will expire at: {expire.isoformat()}")
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Decoded payload: {payload}")
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)




