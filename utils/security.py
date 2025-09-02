from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from tools.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_reset_token(email: str):
    expire = datetime.now() + timedelta(hours=1)
    to_encode = {"email":email, "exp": expire}
    token =  jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("email")
    except:
        return None

hashed = hash_password("mysecret")
email = "harrydoe@gmail.com"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImhhcnJ5ZG9lQGdtYWlsLmNvbSIsImV4cCI6MTc1NjgzMjA2MH0.MZjvxwpDwet4d9by8clek5ejV6UlH6JvcN9nMHRSTUI"
print("Hashed:", hashed)
print("Verify ok?", verify_password("mysecret", hashed))
print("Verify fail?", verify_password("wrong", hashed))
print("reset token", create_reset_token(email))
print("verify reset token", verify_reset_token(token))

