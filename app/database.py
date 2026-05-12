import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/feedback_admin",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def ensure_database_exists() -> None:
    url = make_url(DATABASE_URL)
    if not url.get_backend_name().startswith("postgresql") or not url.database:
        return

    database_name = url.database
    server_url = url.set(database="postgres")
    server_engine = create_engine(
        server_url,
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )

    try:
        with server_engine.connect() as connection:
            exists = connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": database_name},
            )
            if not exists:
                escaped_name = database_name.replace('"', '""')
                connection.execute(text(f'CREATE DATABASE "{escaped_name}"'))
    finally:
        server_engine.dispose()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
