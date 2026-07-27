import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent

# Configured paths
REPORTS_DIR = BASE_DIR / "reports"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Create directories if they do not exist
for directory in [REPORTS_DIR, DATABASE_DIR, LOGS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# Model
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_DIR}/research.db").strip()

# Server Host and Port
HOST = os.getenv("HOST", "127.0.0.1").strip()
PORT = os.getenv("PORT", "8000").strip()


# Demo Mode (Simulate runs if API keys are missing)
DEMO_MODE_ENV = os.getenv("DEMO_MODE", "True").strip().lower()
DEMO_MODE = DEMO_MODE_ENV in ("true", "1", "yes") or not GROQ_API_KEY or not TAVILY_API_KEY

# Print warning if in demo mode
if DEMO_MODE:
    print("[!] AI Research Team running in DEMO_MODE (Simulated agent executions). Configure GROQ_API_KEY and TAVILY_API_KEY in .env to run live API calls.")
else:
    print("[*] AI Research Team running in LIVE API mode.")
