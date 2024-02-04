from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from private_gpt.config import Config

# DATABASE_URL = "postgresql://chenbingxiang:6822688@localhost:5432/thesis"
DATABASE_URL = Config.DATABASE_URL
engine: Engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# Dependency
def get_db() -> Session:
    """
    Generate a new database session for FastAPI dependencies.

    Yields:
        Session: The generated database session.

    Notes:
        This function should be used as a dependency in FastAPI routes.
        It creates a new session that can be used in a route, and ensures
        the session is closed after the route function finishes execution.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
