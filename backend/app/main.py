from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import database  

# Lifespan event to initialize the database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.init_db()
        print("successfully initialized the database.")
    except Exception as e:
        print(f"Failed to initialize the database: {e}")
    
    yield

app = FastAPI(
    title="DB Project API",
    lifespan=lifespan
)

@app.get("/healthcheck")
def health_check(db: Session = Depends(database.get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "ok"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )