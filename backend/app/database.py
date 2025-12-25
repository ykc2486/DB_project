import os
import time
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from . import models

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

POSTGRES_USER = os.getenv("POSTGRES_USER", "").strip()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "").strip()
POSTGRES_DB = os.getenv("POSTGRES_DB", "").strip()

if not POSTGRES_USER:
    raise OSError("POSTGRES_USER environment variable is not set.")

RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "true"

# Allow overriding host and port via environment variables
DB_HOST = os.getenv("POSTGRES_HOST")
if not DB_HOST:
    DB_HOST = "postgres_db" if RUNNING_IN_DOCKER else "localhost"

DB_PORT = os.getenv("POSTGRES_PORT")
if not DB_PORT:
    DB_PORT = "5432" if RUNNING_IN_DOCKER else "5433"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    initialize the database tables with retries.
    """
    retries = 5
    while retries > 0:
        try:
            print(f"Connecting to {DB_HOST}:{DB_PORT} to initialize database tables...")
            with engine.connect() as connection:
                for statement in models.CREATE_TABLE_STATEMENTS:
                    connection.execute(text(statement))
                connection.commit()
            print("Database tables initialized.")
            break
        except OperationalError as e:
            retries -= 1
            print(f"Database connection failed. Retrying in 2 seconds... ({retries} retries left)")
            if retries == 0:
                print(f"Final Error: {e}")
                raise e
            time.sleep(2)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
