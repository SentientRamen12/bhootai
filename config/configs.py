import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Database paths
SQLITE_DB_PATH = DATA_DIR / "sqlite" / "game.db"
CHROMADB_PATH = DATA_DIR / "chromadb"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # openai, anthropic, gemini
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LLM Model Configuration
LLM_MODELS = {
    "openai": os.getenv("OPENAI_MODEL", "gpt-4"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
    "gemini": os.getenv("GEMINI_MODEL", "gemini-pro")
}

# Ensure directories exist
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
CHROMADB_PATH.mkdir(parents=True, exist_ok=True) 