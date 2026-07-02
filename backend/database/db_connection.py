"""
db_connection.py
Sets up the SQLAlchemy engine/session for MySQL, and provides the
get_db() dependency used by every FastAPI route to talk to the database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and always closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
