from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "polymarket_assistant"
    gemini_api_key: str = ""
    backend_url: str = "http://localhost:8000"
    cors_origins: List[str] = ["http://localhost:3000", "chrome-extension://*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
