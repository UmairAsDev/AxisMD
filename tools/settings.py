from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30


    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
