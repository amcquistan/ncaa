import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_BASE_URL = "https://api.collegefootballdata.com"
CFBD_API_KEY = os.getenv("CFBD_API_KEY", "")
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
