# database/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Database URL (SQLite file named 'app.db' in the project root)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# 2. Create the Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} 
)

# 3. Create a Session Local factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Base Class for models
Base = declarative_base()

def get_db():
    """Dependency function to yield a database session (for FastAPI/Flask)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()