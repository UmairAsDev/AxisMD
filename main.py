from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError

from controller.auth.auth import router as auth_router
from controller.users.users import router as user_router
from tools.settings import settings  # 👈 make sure this points to your auth.py
from utils.jwt_handler import verify_access_token


app = FastAPI()

# 🔹 JWT Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Allow unauthenticated access to login/registration routes
    if request.url.path.startswith("/auth/login") or request.url.path.startswith("/auth/signup"):
        return await call_next(request)

    # You can allow other public routes here too
    if request.url.path == "/open-api":
        return await call_next(request)

    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})

    token = auth_header.split(" ")[1]
    try:
        payload = verify_access_token(token)
        request.state.user = payload
    except JWTError:
        return JSONResponse(status_code=403, content={"detail": "Invalid or expired token"})

    return await call_next(request)


# 🔹 Include Routers
app.include_router(auth_router)
app.include_router(user_router)


# 🔹 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔹 Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True) 
