from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    APP_NAME: str = "Cortex"
    VERSION: str = "0.1.0"
    
    # LLM Choice
    LLM_PROVIDER: Literal["openai", "huggingface", "ollama", "gemini"] = "openai"
    
    # OpenAI / Groq / LlamaAPI / Local
    LLM_API_KEY: str | None = None
    LLM_BASE_URL: str | None = None
    LLM_MODEL: str = "gpt-3.5-turbo" # Default
    
    # Hugging Face
    HUGGINGFACEHUB_API_TOKEN: str | None = None
    
    # Paths
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
