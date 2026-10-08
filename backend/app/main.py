from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.api.analysis import router as analysis_router
from backend.app.db.connection import get_db


app = FastAPI(
    title="AI Data Analyst",
    description="Natural language data analysis with Text-to-SQL and clarification",
    version="0.1.0",
)


app.include_router(analysis_router)


@app.get("/")
def root():
    return {"message": "AI Data Analyst API is running"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}