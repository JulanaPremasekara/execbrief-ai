import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[5]
load_dotenv(ROOT / ".env.local", override=False)
DATA_ROOT = ROOT / "data" / "synthetic"
def database_url():
    value = os.getenv("DATABASE_URL", "")
    if not value:
        raise ValueError("Configure DATABASE_URL locally in .env.local")
    return value

