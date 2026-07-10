import os
from pathlib import Path


def load_env_file(env_path = ".env"):
    path = Path(env_path)
    if not path.is_file():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


load_env_file()

SECRET_KEY = os.environ.get("SECRET_KEY", "something")

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")

GOOGLE_AUTH_URL = os.environ.get(
    "GOOGLE_AUTH_URL",
    "https://accounts.google.com/o/oauth2/v2/auth"
)

GOOGLE_TOKEN_URL = os.environ.get(
    "GOOGLE_TOKEN_URL",
    "https://oauth2.googleapis.com/token"
)

GOOGLE_USERINFO_URL = os.environ.get(
    "GOOGLE_USERINFO_URL",
    "https://www.googleapis.com/oauth2/v2/userinfo"
)

REDIRECT_URI = os.environ.get(
    "REDIRECT_URI",
    "http://127.0.0.1:5000/callback"
)

DB_PATH = "./db/e_commerce.db"
SQL_INIT_FILE = "./db/db.sql"