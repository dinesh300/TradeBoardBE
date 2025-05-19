from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Patch for old-style Heroku URL that uses 'postgres://' instead of 'postgresql://'
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://uea92tbr2locmp:pa9348c6b2ab9a1fd6213b241ff910cb599cb91f377643bfd94d40577b556d638@cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/diu33807jin5b"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
