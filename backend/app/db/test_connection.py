from sqlalchemy import text

from backend.app.db.connection import engine


with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))

    print("Database connection successful!")
    print(f"Result: {result.scalar()}")