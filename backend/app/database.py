import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# app/database.py
POSTGRES_USER = os.getenv("POSTGRES_USER").strip()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD").strip()
POSTGRES_DB = os.getenv("POSTGRES_DB").strip()

print("--- debug ---")
print(f"User: [{POSTGRES_USER}]")
print(f"Pass: [{POSTGRES_PASSWORD}]")
print(f"DB  : [{POSTGRES_DB}]")
print("---------------")

if not POSTGRES_USER:
    raise OSError("POSTGRES_USER environment variable is not set.")

DB_HOST = "127.0.0.1" if os.getenv("RUNNING_IN_DOCKER") != "true" else "postgres_db"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5433/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()