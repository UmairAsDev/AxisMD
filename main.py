from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError

from controller.auth.auth import router as auth_router
from controller.users.users import router as user_router
from controller.notes.notes import router as notes_router
from controller.patient.patient import router as patient_router
from tools.settings import settings 
from utils.jwt_handler import verify_access_token


app = FastAPI()

# 🔹 JWT Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    PUBLIC_ROUTES = [
        "/auth/login",
        "/auth/signup",
        "/auth/forgot_password",
        "/auth/reset_password",
        "/open-api",
        "/docs",         
        "/openapi.json",  
        "/redoc",         
        "/favicon.ico"    
    ]


    if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
        return await call_next(request)

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
app.include_router(notes_router)
app.include_router(patient_router)


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
