import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

POSTGRES_USER = os.getenv("POSTGRES_USER", "").strip()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "").strip()
POSTGRES_DB = os.getenv("POSTGRES_DB", "").strip()

if not POSTGRES_USER:
    raise OSError("POSTGRES_USER environment variable is not set.")

RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "true"
DB_HOST = "postgres_db" if RUNNING_IN_DOCKER else "127.0.0.1"
DB_PORT = "5432" if RUNNING_IN_DOCKER else "5433"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """
    initialize the database tables.
    """
    
    print(f"Connecting to {DB_HOST}:{DB_PORT} to initialize database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()