from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.auth.auth import router as auth_router
from controller.users.users import router as user_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True) 
