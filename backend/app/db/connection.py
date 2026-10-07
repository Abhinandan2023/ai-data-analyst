from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_username: str
    database_password: str
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str
    groq_api_key: str

    model_config= SettingsConfigDict(env_file=".env")

settings = Settings()


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()