from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:123@localhost:5432/diplom_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Все остальные модели будут наследоваться от него

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()