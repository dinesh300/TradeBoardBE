from app.database_pg import Base, engine

# Import all your models so they get registered with Base.metadata
from app.models import *  # Adjust import based on your project structure

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
