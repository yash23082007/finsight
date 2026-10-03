from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

configured_database_url = os.getenv("DATABASE_URL")
if os.getenv("VERCEL") and (
    not configured_database_url or configured_database_url.startswith("sqlite:///data/")
):
    DATABASE_URL = "sqlite:////tmp/finsight.db"
elif configured_database_url:
    DATABASE_URL = configured_database_url
else:
    DATABASE_URL = "sqlite:///data/processed/finsight.db"

if DATABASE_URL.startswith("sqlite:///data/"):
    os.makedirs("data/processed", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
