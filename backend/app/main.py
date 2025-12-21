from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import database
from . import models, routes
from fastapi.middleware.cors import CORSMiddleware

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount application routes
app.include_router(routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the DB Project API"}

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
