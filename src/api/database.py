"""
Database connection and session management using SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.api.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connection before using
    echo=settings.DATABASE_ECHO  # Log SQL queries if enabled
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """
    Dependency for database session.
    Yields session and ensures cleanup.
    Auto-rollback on exception.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit if no exception
    except Exception as e:
        db.rollback()  # Rollback on exception
        logger.error(f"Database transaction rolled back: {e}")
        raise
    finally:
        db.close()
