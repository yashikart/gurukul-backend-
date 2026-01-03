
import sys
import os

# Add CWD to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import SQLALCHEMY_DATABASE_URL

print(f"--- Configuration Debug ---")
print(f"CWD: {os.getcwd()}")
print(f"Settings DATABASE_URL: {settings.DATABASE_URL}")
print(f"Effective SQLME URL: {SQLALCHEMY_DATABASE_URL}")
