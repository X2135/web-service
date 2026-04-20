import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _normalize_database_url(url: str) -> str:
    # Render sometimes provides postgres://; SQLAlchemy expects postgresql://.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Use psycopg (v3) explicitly when no driver is specified.
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Managed PostgreSQL providers typically require SSL.
    if url.startswith("postgresql+") and "sslmode=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"

    return url


APP_ENV = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower()
raw_database_url = os.getenv("DATABASE_URL")

if APP_ENV in {"production", "prod"} and not raw_database_url:
    raise RuntimeError(
        "DATABASE_URL is required when APP_ENV/ENVIRONMENT is set to production. "
        "SQLite fallback is disabled in production mode."
    )

DATABASE_URL = _normalize_database_url(raw_database_url or "sqlite:///./habits.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
