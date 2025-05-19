from app.database_pg import engine, Base
from app.models import *
#from app.models import TickerData, SubscribedSymbol, AnomalyEntry,AnomalyTicker
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL tables created successfully.")

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")

#if __name__ == "__main__":
    #reset_database()
if __name__ == "__main__":
    create_tables()
