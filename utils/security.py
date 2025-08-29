from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



hashed = hash_password("mysecret")
print("Hashed:", hashed)
print("Verify ok?", verify_password("mysecret", hashed))
print("Verify fail?", verify_password("wrong", hashed))
