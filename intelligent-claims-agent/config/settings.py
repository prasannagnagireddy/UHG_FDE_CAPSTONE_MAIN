from dataclasses import dataclass
from dotenv import load_dotenv
import os
load_dotenv()
@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql://claims:claims@localhost:5432/claimsdb")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    llm_enabled: bool = os.getenv("LLM_ENABLED", "false").lower() == "true"
    mailpit_url: str = os.getenv("MAILPIT_URL", "http://localhost:8025")
settings = Settings()
