from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger(__name__)

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args={} # Add SSL args here for production DBs
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection successful.")
except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    # You might want to exit the application if the DB connection fails at startup
    # raise e

def get_db():
    """
    Dependency function to get a database session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
