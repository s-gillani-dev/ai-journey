# DineFlow/config/settings.py
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()  # <-- loads .env automatically

class Settings(BaseModel):
    OPENAI_API_KEY: str
    ENV: str = "local"

def load_settings() -> Settings:
    return Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        ENV=os.getenv("ENV", "local"),
    )

settings = load_settings()

