import os

from dotenv import load_dotenv

load_dotenv(".env")
TG_API_TOKEN = os.environ.get("TG_API_TOKEN")
DB_URL = os.environ.get("DB_URL")
