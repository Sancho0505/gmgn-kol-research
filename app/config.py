import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://gmgn:gmgn_password@localhost:5433/gmgn_research")
GMGN_API_KEY = os.getenv("GMGN_API_KEY", "")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")
