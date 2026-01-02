
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "Gurukul Backend API"
    HOST: str = "0.0.0.0"
    PORT: int = 3000
    RELOAD: bool = True
    
    # API Keys
    GROQ_API_KEY: Optional[str] = None
    GROQ_API_ENDPOINT: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"
    
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_PRIMARY: str = "llama2"
    LOCAL_LLAMA_API_URL: str = "http://localhost:8080/v1/chat/completions"
    
    YOUTUBE_API_KEY: Optional[str] = None
    YOUTUBE_API_BASE_URL: str = "https://www.googleapis.com/youtube/v3/search"

    # Database
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None # postgresql://user:password@host:port/db

    # Feature Flags
    PDF_SUPPORT: bool = True
    DOC_SUMMARIZER_SUPPORT: bool = False
    PDF_SUMMARIZER_SUPPORT: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
