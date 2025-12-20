from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database

app = FastAPI(title="DB Project API")

@app.get("/healthcheck")
def health_check(db: Session = Depends(database.get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "success", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
