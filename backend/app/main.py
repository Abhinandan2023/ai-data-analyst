from fastapi import FastAPI

app=FastAPI( title="AI Data Analyst",
    description="Natural language data analysis with Text-to-SQL and clarification",
    version="0.1.0",
    )

@app.get("/")
def root():
    return{
        "message": "AI Data Analyst API is running"
    }

@app.get("/health")
def health():
    return{
        "status": "healthy"
    }