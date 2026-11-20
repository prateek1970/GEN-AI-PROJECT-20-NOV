"""
Configuration settings for Silicon Odyssey: Founder Intelligence RAG.
Loads API keys and settings from backend/.env safely.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Safe .env loader
def _load_env_file(path: Path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val

_load_env_file(ENV_PATH)

# Directory configurations with environment variable overrides
DATA_DIR_VAL = os.environ.get("DATA_DIR", "./data")
DATA_DIR = (BASE_DIR / DATA_DIR_VAL).resolve() if not Path(DATA_DIR_VAL).is_absolute() else Path(DATA_DIR_VAL)

STORAGE_DIR = BASE_DIR / "storage"

CHROMA_PATH_VAL = os.environ.get("CHROMA_PATH", "./storage/chroma")
CHROMA_DB_DIR = (BASE_DIR / CHROMA_PATH_VAL).resolve() if not Path(CHROMA_PATH_VAL).is_absolute() else Path(CHROMA_PATH_VAL)

# If chroma directory doesn't exist but chroma_db does, prioritize the populated database
if not CHROMA_DB_DIR.exists() and (STORAGE_DIR / "chroma_db").exists():
    CHROMA_DB_DIR = STORAGE_DIR / "chroma_db"

DEFAULT_PDF_PATH = DATA_DIR / "silicon_odyssey_founder_autobiography_50p.pdf"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# Google Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
GEMINI_CHAT_MODEL = os.environ.get("GEMINI_CHAT_MODEL") or os.environ.get("GEMINI_MODEL") or "gemini-3.8-flash"
GEMINI_MODEL = GEMINI_CHAT_MODEL
GEMINI_EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL") or "gemini-embedding-2"

# RAG & Chunking Parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 5
RRF_K = 60
BOILERPLATE_PENALTY = 0.85
MIN_BM25_THRESHOLD = 1.0
